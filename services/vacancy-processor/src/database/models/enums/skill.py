from database.models.enums import BaseAliasEnum


__all__ = ["SkillEnum"]


class SkillEnum(BaseAliasEnum):
    __validate_ordering__ = True

    UNKNOWN = "Неизвестно"

    ACTIVE_DIRECTORY = "Active Directory"
    AGILE = "Agile"
    AIOGRAM = "aiogram"
    AIOHTTP = "aiohttp"
    ALLURE = "Allure", ("allure testops",)
    ANDROID = "Android"
    ANGULAR = "Angular"
    ANSIBLE = "Ansible"
    APACHE = "Apache"
    APACHE_AIRFLOW = "Apache Airflow", ("airflow",)
    APACHE_KAFKA = "Apache Kafka", ("kafka",)
    APACHE_NIFI = "Apache NiFi", ("nifi",)
    APACHE_SPARK = "Apache Spark", ("spark", "pyspark")
    APACHE_SUPERSET = "Apache Superset", ("superset",)
    ARGOCD = "ArgoCD"
    ASP_NET = "ASP.NET"
    ASP_NET_CORE = "ASP.NET Core"
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
    CISCO = "Cisco"
    CLICKHOUSE = "ClickHouse"
    CMS = "CMS"
    COMPUTER_VISION = "Computer Vision"
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
    DWH = "DWH"
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
    KANBAN = "Kanban"
    KIBANA = "Kibana"
    KOTLIN = "Kotlin"
    KUBERNETES = "Kubernetes"
    LANGCHAIN = "LangChain"
    LARAVEL = "Laravel"
    LINUX = "Linux", ("ubuntu", "debian", "centos", "unix", "macos")
    LLM = "LLM"
    MACHINE_LEARNING = "Machine Learning", ("ml",)
    MARIA_DB = "MariaDB"
    MAVEN = "Maven"
    MICROSERVICES = "Микросервисы", ("микросервисная архитектура", "microservices")
    MIKROTIK = "MikroTik"
    MIRO = "Miro"
    MLFLOW = "MLflow"
    MOBX = "MobX"
    MONGODB = "MongoDB"
    MS_OFFICE = (
        "MS Office",
        ("ms powerpoint", "word", "microsoft excel", "powerpoint", "ms windows", "ms word", "ms excel"),
    )
    MS_SQL = "MS SQL", ("ms sql server", "mssql")
    MYSQL = "MySQL"
    NESTJS = "NestJS", ("nest.js",)
    NEXT_JS = "Next.js", ("nextjs",)
    NGINX = "Nginx"
    NLP = "NLP"
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
    POSTGRES = "PostgreSQL", ("postgres", "postgress")
    POWER_BI = "Power BI"
    POWER_QUERY = "Power Query"
    POWERSHELL = "PowerShell"
    PROMETHEUS = "Prometheus"
    PROXMOX = "Proxmox"
    PYDANTIC = "Pydantic"
    PYTEST = "pytest"
    PYTHON = "Python", ("python 3.x", "python 3", "async python")
    PYTORCH = "PyTorch"
    QA = "QA"
    R = "R"
    RABBITMQ = "RabbitMQ", ("rabbit mq",)
    REACT = "React", ("reactjs", "react hooks", "react.js")
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
    SPRING = "Spring", ("spring framework",)
    SPRING_BOOT = "Spring Boot", ("java spring boot",)
    SQL = "SQL", ("реляционные базы данных",)
    SQLALCHEMY = "SQLAlchemy"
    STL = "STL"
    SWIFT = "Swift"
    SYMFONY = "Symfony"
    TABLEAU = "Tableau"
    TAILWIND = "Tailwind"
    TCP_IP = "TCP/IP", ("tcp",)
    TDD = "TDD"
    TEAM_CITY = "TeamCity"
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
    WATERFALL = "Waterfall"
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
