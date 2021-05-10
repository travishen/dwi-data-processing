from environs import Env

env = Env()
env.read_env()

DATABASES = {
    'default': {
        'ENGINE': 'postgresql',
        'HOST': env.str('POSTGRES_HOST'),
        'PORT': env.int('POSTGRES_PORT'),
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'OPTIONS': {},
    },
}
