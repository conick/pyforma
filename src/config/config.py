import os
from pydantic import BaseSettings
from pydantic.env_settings import BaseSettings, SettingsSourceCallable
from typing import Optional
from yaml_settings_pydantic import create_yaml_settings

ROOT_DIR = os.path.abspath(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
) + '/'

class JobConfig(BaseSettings):
    interval_seconds: int
    is_enabled: bool = True
    options: Optional[BaseSettings] = None

class JobExcelLockerOptions(BaseSettings):
    source_publication_alias: str
    complete_publication_alias: str
    portion: int = 5
    completed_folder: Optional[str] = None
    unlock_columns: Optional[list[str]] = None
    auto_filter: bool = False

class JobExcelLockerConfig(JobConfig):
    options: JobExcelLockerOptions

class FormaConfig(BaseSettings):
    address: str
    user_name: str
    password: str
    token_valid_minutes: int = 5

class JobsConfig(BaseSettings):
    excel_locker: JobExcelLockerConfig

class CliLogConfig(BaseSettings):
    is_enabled: bool = True
    level: str = 'debug'

class FileLogConfig(BaseSettings):
    is_enabled: bool = False
    level: str = 'info'
    name: str = 'app.log'
    folder: str = ROOT_DIR + '../'

class LogConfig(BaseSettings):
    cli: CliLogConfig = CliLogConfig()
    file: FileLogConfig = FileLogConfig()

class Config(BaseSettings):
    log: LogConfig = LogConfig()
    forma: FormaConfig
    jobs: Optional[JobsConfig]

    class Config :
        env_settings_yaml = create_yaml_settings(
            ROOT_DIR + '../config.yaml'
        )

        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ):
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                cls.env_settings_yaml,
            )

config = Config()

