from parsers.schemas import TelegramChannelUrl


__all__ = ["channel_links"]


channel_usernames: set[str] = {
    "ai_rabota",
    "csharpdevjob",
    "datajobschannel",
    "datascienceml_jobs",
    "datascjobs",
    "de_rabota",
    "devs_it",
    "dotnetrujobsfeed",
    "easy_python_job",
    "golangjobsit",
    "hr_itwork",
    "it_match_python",
    "java_workit",
    "javascriptjobjs",
    "job_javadevs",
    "job_python",
    "job_react",
    "python_djangojobs",
    "qa_chillout_jobs",
    "rabotaj_razrabotchik",
    "uzdev_jobs",
    "workayte",
    "yotolabpython",
}

channel_links: set[TelegramChannelUrl] = {TelegramChannelUrl.create(u) for u in channel_usernames}
