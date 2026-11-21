# Job Radar

Feeds the page at https://www.sudhakarchundu.org/jobs/radar/.

`.github/workflows/jobradar.yml` runs `publish.py` every 3 hours. It reads the careers sites listed in
`config.json` (Ashby, Greenhouse, Workday, SmartRecruiters, Eightfold, AMD, Google, Apple, ASML), scores each
job for role fit (0 to 100), writes `jobs/radar/data/jobs.json`, and emails new matches.

- Change roles, skills, weights, companies or blocked companies in `config.json`.
- Email needs the repository secret `JOBRADAR_GMAIL_APP_PASSWORD` (a Gmail app password for the `from`
  address in `config.json`). Without it the page still updates; only the email is skipped.
- State (which jobs were already emailed) lives in a SQLite file kept in the Actions cache. If the cache is
  lost, it is rebuilt from the last published `jobs.json`, so old jobs are not emailed again.
- Run locally: `python tools/jobradar/publish.py --no-email`
