from database.models.enums import BaseAliasEnum


__all__ = ["SkillEnum"]


class SkillEnum(BaseAliasEnum):
    __validate_ordering__ = True

    UNKNOWN = "Неизвестно"

    ACTIVE_DIRECTORY = "Active Directory"
    AIOGRAM = "aiogram"
    AIOHTTP = "aiohttp"
    AIRFLOW = "Airflow", ("apache airflow",)
    ALLURE = "Allure"
    ANDROID = "Android"
    ANGULAR = "Angular"
    ANSIBLE = "Ansible"
    ARGOCD = "ArgoCD"
    ASP_NET = "ASP.NET"
    ASYNCIO = "asyncio"
    AXIOS = "Axios"
    AZURE = "Azure", ("azure devops",)
    BAN = "Ban", ("banjs", "ban.js")
    BASH = "Bash"
    BIG_DATA = "Big Data", ("работа с большим объемом информации",)
    BITRIX = "Bitrix", ("битрикс", "битрикс 24", "битрикс24", "bitrix24")
    BPMN = "BPMN"
    C = "C"
    C_SHARP = "C#", ("csharp",)
    CASSANDRA = "Cassandra"
    CELERY = "Celery"
    CI_CD = "CI/CD", ("gitlab ci", "gitlab ci/cd", "github actions")
    CLICKHOUSE = "ClickHouse"
    CMS = "CMS"
    CONFLUENCE = "Confluence", ("atlassian confluence",)
    CPP = "C++", ("cpp",)
    CRM = "CRM"
    CSS = "CSS", ("css3",)
    CYPRESS = "Cypress"
    DART = "DART"
    DAX = "DAX"
    DEVOPS = "DevOps", ("dev/ops",)
    DHCP = "DHCP"
    DJANGO = "Django", ("drf", "django orm", "django rest framework", "django rest")
    DNS = "DNS"
    DOCKER = "Docker", ("docker-compose", "docker compose")
    DOT_NET = ".NET", (".net core", ".net framework")
    ELASTICSEARCH = "Elasticsearch", ("elk", "elk stack")
    ENGLISH = "Английский язык"
    ETL = "ETL"
    EXCEL = "Excel"
    EXCHANGE = "Exchange", ("ms exchange",)
    EXPRESS = "Express"
    FAST_API = "FastAPI"
    FIDDLER = "Fiddler"
    FIGMA = "Figma"
    FLASK = "Flask"
    FLUTTER = "Flutter"
    GCP = "GCP", ("google cloud platform", "google cloud")
    GIT = "Git", ("github", "gitlab")
    GO = "Go", ("golang",)
    GOOGLE_SHEETS = "Google Sheets"
    GPO = "GPO", ("group policy", "group policy object")
    GRADLE = "Gradle"
    GRAFANA = "Grafana"
    GRAPHQL = "GraphQL"
    GREENPLUM = "Greenplum"
    GRPC = "gRPC"
    GULP = "Gulp"
    GUNICORN = "Gunicorn"
    HADOOP = "Hadoop"
    HELM = "Helm"
    HIBERNATE = "Hibernate"
    HIVE = "Hive"
    HTML = "HTML", ("html5",)
    HTTP = "HTTP", ("https", "http/https")
    HYPER_V = "Hyper-V"
    IOS = "iOS"
    JAVA = "Java"
    JAVASCRIPT = "JavaScript"
    JENKINS = "Jenkins"
    JEST = "Jest"
    JIRA = "Jira", ("atlassian jira",)
    JQUERY = "jQuery"
    JSON = "JSON"
    JUNIT = "JUnit"
    JWT = "JWT"
    KAFKA = "Kafka", ("apache kafka",)
    KANBAN = "Kanban"
    KIBANA = "Kibana"
    KOTLIN = "Kotlin"
    KUBERNETES = "Kubernetes"
    LANGCHAIN = "LangChain"
    LARAVEL = "Laravel"
    LINUX = "Linux", ("ubuntu", "debian", "centos", "unix", "macos")
    LLM = "LLM"
    MACHINE_LEARNING = "Machine Learning", ("ml",)
    MAVEN = "Maven"
    MICROSERVICES = "Микросервисы"
    MIKROTIK = "MikroTik"
    MIRO = "Miro"
    MLFLOW = "MLflow"
    MOBX = "MobX"
    MONGODB = "MongoDB"
    MS_OFFICE = (
        "MS Office",
        ("ms powerpoint", "word", "microsoft excel", "powerpoint", "ms windows", "ms word", "ms excel"),
    )
    MYSQL = "MySQL"
    NESTJS = "NestJS", ("nest.js",)
    NEXT_JS = "Next.js", ("nextjs",)
    NGINX = "Nginx"
    NODE_JS = "Node.js", ("nodejs",)
    NOSQL = "NoSQL"
    NUMPY = "Numpy"
    NUXT_JS = "Nuxt.js", ("nuxt",)
    ONE_C = "1С", ("1c", "1с: предприятие", "1c: предприятие", "1c: erp", "1с:erp", "1с программирование")
    OOP = "ООП", ("oop",)
    OPENAI = "OpenAI", ("openai api",)
    OPENSHIFT = "OpenShift"
    OPENSTACK = "OpenStack"
    ORACLE = "Oracle"
    PANDAS = "pandas"
    PHP = "PHP"
    PLAYWRIGHT = "Playwright"
    POSTGIS = "PostGIS"
    POWER_BI = "Power BI"
    POWER_QUERY = "Power Query"
    POWERSHELL = "PowerShell"
    PROMETHEUS = "Prometheus"
    PROXMOX = "Proxmox"
    PYDANTIC = "Pydantic"
    PYTEST = "pytest"
    PYTHON = "Python", ("python 3.x", "python 3")
    PYTORCH = "PyTorch"
    QA = "QA"
    R = "R"
    RABBITMQ = "RabbitMQ"
    REACT = "React", ("reactjs", "react hooks")
    REACT_NATIVE = "React Native"
    REDIS = "Redis"
    REDUX = "Redux", ("redux toolkit",)
    REQUESTS = "requests"
    REST_API = "REST API", ("rest", "api", "restful api", "restful", "swagger", "postman")
    RPC = "RPC", ("grpc",)
    RUBY = "Ruby"
    RUST = "Rust"
    RXJS = "RxJS"
    S3 = "S3", ("aws s3", "aws")
    SCALA = "Scala"
    SCIKIT_LEARN = "Scikit-learn", ("scikit learn",)
    SCRUM = "SCRUM"
    SCSS = "SCSS", ("sass",)
    SELENIUM = "Selenium"
    SENTRY = "Sentry"
    SEO = "SEO"
    SOAP = "SOAP"
    SOLID = "SOLID"
    SPA = "SPA"
    SPARK = "Spark", ("apache spark", "pyspark")
    SPRING = "Spring", ("spring framework",)
    SPRING_BOOT = "Spring Boot", ("java spring boot",)
    SQL = "SQL", ("postgres", "postgresql", "ms sql server", "mssql", "ms sql")
    SQLALCHEMY = "SQLAlchemy"
    SWIFT = "Swift"
    SYMFONY = "Symfony"
    TABLEAU = "Tableau"
    TAILWIND = "Tailwind"
    TCP_IP = "TCP/IP"
    TENSORFLOW = "TensorFlow"
    TERRAFORM = "Terraform"
    TYPESCRIPT = "TypeScript", ("ts",)
    UML = "UML"
    UNITTEST = "unittest", ("unit testing", "unit test")
    UX_UI = "UX/UI", ("ui/ux", "ui", "ux")
    VITE = "Vite"
    VLAN = "VLAN"
    VMWARE = "VMware"
    VPN = "VPN"
    VUE_JS = "Vue.js", ("vue", "vuejs")
    VUEX = "Vuex"
    WEBPACK = "Webpack"
    WEBSOCKET = "WebSocket", ("websockets",)
    WINDOWS = "Windows"
    WINDOWS_SERVER = "Windows Server"
    XML = "XML"
    YANDEX_CLOUD = "Yandex Cloud"
    YII2 = "Yii2", ("yii",)
    ZABBIX = "Zabbix"
    ZUSTAND = "Zustand"
    # TODO: добавить проверку, что паттерны не совпадают с алиасами
    __ignore_patterns__ = (
        "adobe",
        "администр",
        "аналитик",
        "анализ",
        "управл",
        "делов",
        "развитие",
        "организатор",
        "продаж",
        "переговор",
        "перепис",
        "продвиж",
        "привлечен",
        "обуч",
        "ответств",
        "настрой",
        "постанов",
        "финанс",
        "работа",
        "моделир",
        "статист",
        "тестир",
        "визуализ",
        "прототип",
        "инвестиц",
        "объем",
        "маркет",
    )
