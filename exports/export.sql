SELECT 
  accident.date AS acc_date,
  accident.hour AS acc_hour,
  accident.dead AS acc_dead,
  accident.injured AS acc_injured,
  accident.party_no AS acc_party_no,
  accident.gender_no AS acc_gender_no,
  accident.uid AS acc_uid,
  accident.driver_birthday AS acc_driver_birthday,
  accident.birthday AS acc_birthday,
  accident.country AS acc_country,
  accident.town AS acc_town,
  accident.party_address_code AS acc_party_address_code,
  accident.party_country AS acc_party_country,
  accident.party_town AS acc_party_town,
  accident.car_type AS acc_car_type,
  accident.injury_level AS acc_injury_level,
  accident.driver_level AS acc_driver_level,
  accident.drunk_level AS acc_drunk_level,
  accident.hit_and_run AS acc_hit_and_run,
  accident.job AS acc_job,
  accident.cause_type AS acc_cause_type,
  accident.age AS acc_age,
  accident.age_group AS acc_age_group,
  violation.birthday AS vio_birthday,
  violation.date AS vio_date,
  violation.is_recidivist::Integer AS vio_is_recidivist,
  violation.is_patched::Integer AS vio_is_patched,
  divorce.rate AS divorce_rate,
  "old".rate AS old_rate,
  indigenous.rate AS indigenous_rate,
  education.rate AS education_rate,
  income_mid.rate AS income_mid_rate,
  income_avg.rate AS income_avg_rate
FROM
  violation,
  accident
  LEFT OUTER JOIN divorce ON EXTRACT(
    year
    FROM
      accident.date
  ) = divorce.year
  AND accident.party_address_code = divorce.address_code
  LEFT OUTER JOIN "old" ON EXTRACT(
    year
    FROM
      accident.date
  ) = "old".year
  AND accident.party_address_code = "old".address_code
  LEFT OUTER JOIN indigenous ON EXTRACT(
    year
    FROM
      accident.date
  ) = indigenous.year
  AND accident.party_address_code = indigenous.address_code
  LEFT OUTER JOIN education ON EXTRACT(
    year
    FROM
      accident.date
  ) = education.year
  AND accident.party_address_code = education.address_code
  LEFT OUTER JOIN income_mid ON EXTRACT(
    year
    FROM
      accident.date
  ) = income_mid.year
  AND accident.party_address_code = income_mid.address_code
  LEFT OUTER JOIN income_avg ON EXTRACT(
    year
    FROM
      accident.date
  ) = income_avg.year
  AND accident.party_address_code = income_avg.address_code
WHERE
  accident.violation_id = violation.id
ORDER BY accident.date DESC