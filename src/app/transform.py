from datetime import datetime
from hashlib import blake2b
from sqlalchemy import or_, and_, extract
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy import func
from .database.utils import session_scope
from .database.models import Violation, Accident, CountryTown, Divorce, Old, Indigenous, Education, IncomeMid, IncomeAvg


def country_town_old_to_new(country, town):
    country = country.replace('台', '臺')
    town = town.replace('台', '臺')
    if country in ('臺中縣', '臺南縣', '高雄縣', '桃園縣'):
        return country.replace('縣', '市'), town[:-1] + '區'
    if country == '臺北縣':
        return '新北市', town[:-1] + '區'
    return country, town


def patch_party_address_from_accident():
    """If party address fields are not complete, patch from accident address."""

    # create lookup mapping
    with session_scope() as s:
        map_qs = s.query(CountryTown.code, CountryTown.country, CountryTown.town).distinct()

    mapping = {
        country+town: code for code, country, town in map_qs
    }

    with session_scope() as s:
        qs = s.query(Accident).filter(
            or_(
                Accident.party_country.is_(None),
                Accident.party_town.is_(None)
            )
        )
        for obj in qs:
            country, town = country_town_old_to_new(obj.country, obj.town)
            lookup_key = f'{country}{town}'
            lookup_code = mapping.get(lookup_key, None)
            if lookup_code:
                obj.party_address_code = lookup_code
                obj.party_country = country
                obj.party_town = town
                obj.is_party_address_patched = True

        # bulk update
        s.flush()


def patch_birthday_from_violation():
    with session_scope() as s:
        qs = s.query(Violation.uid, Violation.birthday).filter(
            Violation.birthday.isnot(None),
        ).distinct()
    data = list(qs)
    mapping = {
        uid: birthday for uid, birthday in data
    }
    with session_scope() as s:
        accident_count = s.query(Accident).count()
    chunk = 1000
    with session_scope() as s:
        for idx in range(0, accident_count, chunk):
            accidents = s.query(Accident).filter(Accident.id.between(idx, idx + chunk)).all()
            for accident in accidents:
                birthday = mapping.get(accident.uid)
                if birthday:
                    accident.birthday = birthday
            # bulk update
            s.flush()

    # Update accidents which cannot find birthday from violation, use first day in birth month
    with session_scope() as s:
        qs = s.query(Accident).filter(
            Accident.birthday.is_(None),
        ).distinct()
        data = list(qs)
        for accident in data:
            if accident.birth_year and accident.birth_month:
                accident.birthday = datetime(accident.birth_year, accident.birth_month, 1).date()
                accident.is_birthday_patched = True
        s.flush()


def patch_missing_violation(tolerance=0):
    # stage 1: link the accident, violation with same date
    with session_scope() as s:
        qs = s.query(Accident, Violation).filter(
            Accident.violation_id.is_(None),
            Violation.accident_id.is_(None),
            Accident.uid == Violation.uid,
            Violation.date == Accident.date,
        )
    chunk = 1000
    data = list(qs)
    print(f'Associate Accident, Violation by same uid and date, match count: {len(data)}.')
    with session_scope() as s:
        for idx in range(0, len(data), chunk):
            for accident, violation in data[idx:idx+chunk]:
                accident.violation_id = violation.id
                violation.accident_id = accident.id
            # bulk update
            s.flush()

    # stage 2: link the accident, violation in tolerance delta days
    for i in range(1, tolerance + 1):
        with session_scope() as s:
            qs = s.query(Accident, Violation).filter(
                Accident.violation_id.is_(None),
                Violation.accident_id.is_(None),
                Accident.uid == Violation.uid,
                or_(
                    Violation.date == Accident.date + i,
                    Violation.date == Accident.date - i,
                )
            ).order_by()
        data = list(qs)
        print(f'Associate Accident, Violation by same uid and {i} delta day, match count: {len(data)}.')
        with session_scope() as s:
            for accident, violation in data:
                accident.violation_id = violation.id
                violation.accident_id = accident.id
            # bulk update
            s.flush()

    # stage 3.1: create missing violations
    with session_scope() as s:
        qs = s.query(Accident).filter(
            Accident.violation_id.is_(None),
        )
    data = list(qs)
    violations = [
        Violation(
            date=accident.date,
            uid=accident.uid,
            accident_id=accident.id,
            is_patched=True
        ) for accident in data
    ]
    with session_scope() as s:
        s.bulk_save_objects(violations)

    # stage 3.2: update link from accident
    with session_scope() as s:
        qs = s.query(Accident, Violation).filter(
            Accident.violation_id.is_(None),
            Violation.accident_id == Accident.id,
        )
    chunk = 1000
    data = list(qs)
    with session_scope() as s:
        for idx in range(0, len(data), chunk):
            for accident, violation in data[idx:idx+chunk]:
                accident.violation_id = violation.id
            # bulk update
            s.flush()

    # stage 4: update violation.is_patched to default false
    with session_scope() as s:
        s.query(Violation).filter(Violation.is_patched.is_(None)).update({Violation.is_patched: False})


def calculate_recidivist():
    true_data_pks = list()
    with session_scope() as s:
        qs = s.query(
            Violation.uid,
            func.array_agg(aggregate_order_by(Violation.date, Violation.date)),
            func.array_agg(aggregate_order_by(Violation.id, Violation.date))
        ).group_by(Violation.uid)

        print(f'Unique user count: {qs.count()}')

        for uid, dates, pks in qs:
            # dates already asc sorted
            # calculate intervals between each two dates
            for i in range(1, len(dates)):
                previous, current = dates[i-1:i+1]
                # if intervals less than 5 year, push to true_data
                if (current - previous).days <= 365*5:
                    # push pk
                    true_data_pks.append(pks[i])

    print(f'True data count: {len(true_data_pks)}')

    # Update database field
    with session_scope() as s:
        s.query(Violation).update({Violation.is_recidivist: False})
    with session_scope() as s:
        s.bulk_update_mappings(Violation, [
            {
                'id': pk,
                'is_recidivist': True
            }
            for pk in true_data_pks
        ])


def calculate_age():
    with session_scope() as s:
        accident_count = s.query(Accident).count()
    chunk = 1000
    with session_scope() as s:
        for idx in range(0, accident_count, chunk):
            accidents = s.query(Accident).filter(Accident.id.between(idx, idx + chunk)).all()
            for accident in accidents:
                if accident.birthday:
                    age = int((accident.date - accident.birthday).days / 365.2425)
                    if 15 <= age < 25:
                        age_group = 1
                    elif 25 <= age < 35:
                        age_group = 2
                    elif 35 <= age < 45:
                        age_group = 3
                    elif 45 <= age < 55:
                        age_group = 4
                    elif 55 <= age < 65:
                        age_group = 5
                    elif age > 65:
                        age_group = 6
                    accident.age = age
                    accident.age_group = age_group
            # bulk update
            s.flush()


def get_output_query():
    with session_scope() as s:
        qs = s.query(Accident, Violation, Divorce.rate, Old.rate, Indigenous.rate, Education.rate, Income.rate).filter(
            Accident.violation_id == Violation.id
        ).outerjoin(
            Divorce,
            and_(extract('year', Accident.date) == Divorce.year, Accident.party_address_code == Divorce.address_code)
        ).outerjoin(
            Old,
            and_(extract('year', Accident.date) == Old.year, Accident.party_address_code == Old.address_code)
        ).outerjoin(
            Indigenous,
            and_(extract('year', Accident.date) == Indigenous.year, Accident.party_address_code == Indigenous.address_code)
        ).outerjoin(
            Education,
            and_(extract('year', Accident.date) == Education.year, Accident.party_address_code == Education.address_code)
        ).outerjoin(
            IncomeMid,
            and_(extract('year', Accident.date) == IncomeMid.year, Accident.party_address_code == IncomeMid.address_code)
        ).outerjoin(
            IncomeAvg,
            and_(extract('year', Accident.date) == IncomeAvg.year, Accident.party_address_code == IncomeAvg.address_code)
        )
        return str(qs)


def encrypt_uid():
    with session_scope() as s:
        accident_count = s.query(Accident).count()
        violation_count = s.query(Violation).count()
    chunk = 1000
    with session_scope() as s:
        for idx in range(0, accident_count, chunk):
            accidents = s.query(Accident).filter(Accident.id.between(idx, idx + chunk)).all()
            for accident in accidents:
                accident.uid = 'I-' + blake2b(accident.uid.encode('utf-8'), digest_size=5).hexdigest()
            # bulk update
            s.flush()
    with session_scope() as s:
        for idx in range(0, violation_count, chunk):
            violations = s.query(Violation).filter(Violation.id.between(idx, idx + chunk)).all()
            for violation in violations:
                violation.uid = 'I-' + blake2b(violation.uid.encode('utf-8'), digest_size=5).hexdigest()
            # bulk update
            s.flush()
