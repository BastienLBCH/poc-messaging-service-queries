from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    kafka_bootstrap_server: str
    kafka_group_id: str
    kafka_topic: str

    keycloak_public_key: str
    keycloak_alg: str
    keycloak_client_id: str
    keycloak_username_test: str
    keycloak_username_test_2: str
    keycloak_password_test: str
    keycloak_token_url: str
    keycloak_users_url: str

    env: str

    command_server: str

    model_config = SettingsConfigDict(env_file=".env")


