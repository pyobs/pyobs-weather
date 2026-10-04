# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries for releases before this file existed were generated from commit subjects.

## [2.2.3] - 2026-10-04

- Add MIT LICENSE

## [2.2.2] - 2026-09-29

- Use brand color (blue) as page accent color (#41)

## [2.2.1] - 2026-09-13

- Replace favicon with a custom pyobs Weather icon
- Add CLAUDE.md entry point pointing to specs/ conventions and tooling
- Note v2.2.0 release and issue closure in plan doc

## [2.2.0] - 2026-09-04

- Mark historic-data CSV export plan as merged (PR #38)
- Update plan doc with review follow-up and corrected test counts
- Address review: date validation, inclusive end-date, tz handling, login-gate UX
- Add login-gated historic data CSV export (#6)
- Adapt per-station plot colors to light/dark theme client-side

## [2.1.0] - 2026-09-03

- Serve static files with Whitenoise, drop the nginx container
- docs: mark #33 section 0 done at iag50srv, note the v2.0.0 release

## [2.0.0] - 2026-09-02

- docs: fix #33 plan's group naming to be per-site, not fleet-wide
- feat: add Keycloak login via pyobs-auth
- Add Dependabot auto-merge workflow for patch/minor updates
- Raise requires-python floor to >=3.12, drop <3.13 cap
- Fix RTD build: bump deprecated ubuntu-20.04, add docs/requirements.txt
- Split docs into the web-app shape, unpin Sphinx to match the rest of the fleet
- read version from pyproject.toml instead of hand-maintained constant
- initial commit towards 2.0
- docs: mark frontend modernization plan implemented, closed (#25)
- add sidebar header like other pyobs web projects, drop footer
- show evaluator limits as text in sensors table
- show weather summary in sidebar on all pages
- add sensor icons to sensors table
- fix chart sizing, icon font loading, and add per-sensor icons
- address PR #26 review: fix version lookup, config error handling, /admin routing
- fix ROOT_URL handling, sensor value formatting, and average-station filter in Vue frontend
- add Playwright e2e tests and mark plan progress
- serve Vue SPA from Django, drop old template frontend, build frontend in Docker
- add Vue 3 frontend (frontend-vue) and /api/config/ endpoint
- add specs/ with frontend modernization plan

## [1.3.6] - 2026-07-30

- fixed regexp

## [1.3.5] - 2026-07-30

- use uv

## [1.3.4] - 2026-07-30

- changed ghcr path

## [1.3.3] - 2026-06-16

- cache evaluator instances across evaluate() ticks

## [1.3.2] - 2026-06-16

- reuse a single InfluxDBClient instead of opening one per call
- fixed readme

## [1.3.1] - 2026-06-16

- upgrade gunicorn to 21+ to fix missing pkg_resources error

## [1.3.0] - 2026-06-16

- make WEATHER_SENSORS and WEATHER_PLOTS configurable via env
- update ports: postgres 17, nginx on 8002, gunicorn on 8000
- update README for current stack and deployment
- revert to celery binary directly
- use python -m celery to ensure correct interpreter is used
- split celery worker and beat into separate services
- remove custom network config from docker-compose
- add nginx with static file serving via shared volume
- add db.sqlite3 to .gitignore
- update docker-compose for RabbitMQ and env file config
- switch message broker from Redis to RabbitMQ
- add .env to .gitignore
- move all config into environment variables
- upgrade Django 3.2 → 5.2 and astropy 6 → 7
- removed file
- switch from poetry to uv

## [1.2.0] - 2025-01-14

- auto push to gitlab
- gitlab ci
- .
- added McDvt100 station
- new versions
- added import
- added dewpoint
- no valid value means good weather, need to add "valid" evaluator in case
- only read last 5 minutes
- use Sensor's active flag
- added active field for sensor
- added skymag
- don't plot average station
- fixed bug
- cleaned up
- longer station codes
- cleaned up and introduced INFLUXDB_MEASUREMENT_AVERAGE
- avg measurement name
- added missing files
- fixed not found font
- fixed annotations
- update plots instead of recreating them
- upgrade to chart.js 4
- install mysql client
- plot min/max
- added mysqlclient
- adopted for new influx
- mysql station
- changed evaluators to influx
- aggregation
- working on influx support
- added .dockerignore
- added Dummy
- added gitignore
- delete old
- correction of filename
- added functionality to choose the database
- Changed Database to Influx
- added libmariadbclient-dev-compat
- added pyproject.toml
- added docs
- added methods for dumping good status and sensor values
- added id
- None checking

## [1.1.3] - 2020-12-03

- if there hasn't been a change in weather status within last 24h, return last change

## [1.1.2] - 2020-12-03

- changed version to 1.1.2
- made footer text smaller and added Docker link
- removed areas from individual stations json
- Disabled animations for plots

## [1.1.1] - 2020-11-24

- version 1.1.1
- version 1.1
- sun alt / good weather plot
- format tick marks to 1 float digit
- use ticks min/max instead of time min/max
- removed debug proxies
- check for sensor before updating it
- some options for Chart.js to align plots
- updated Chart.js to v2.9.4
- always show last 24h
- added plot for good weather during last 24h
- update
- Added new table GoodWeather to log changes between good and bad weather
- removed debug proxy config
- exclude average station from status evaluation
- fixed footer
- added footer to page
- new multi-stage docker file
- added backup/restore commands
- fixed bug
- added plot of danger/warning areas
- added annotation plugin for chartjs
- added areas() method
- added possibility to multiply factor to values
- non-existing values are always bad
- made sensor/time combination in Value unique
- only create sensor value, if none exists for given sensor and time
- added migrations
- added JSON station
- deleted migrations
- added indexes
- use nautical twilight instead of astronomical
- renamed value to threshold
- adjusted CSS paths
- added semicolon
- fixed bug (az->alt)
- clean up
- working on new timeline
- fixed root=/ case
- add migration
- added "average" flag for sensors which must be set in order for this sensor to be used in "average" and "current" stations
- timezone again
- timezone handling
- removed debug output
- fixed static root
- updated example config
- root url
- setting default password for postgres
- added new CSV station
- added ROOT_URL setting
- fixed typo
- added more documentation
- updated readme
- added pressure to monet station
- fixed None bug
- fixed path
- fixed static dir
- removed collectstatic from Dockerfile
- new way of setting sensor value
- using latest temp/press/humid for calculating solar elevation
- changed storing of values
- added new McDonald telnet station
- re-enabled sunset and sunrise times
- remove debug output
- added McDonald Archive station
- added skytemp to SENSOR_TYPES
- undo for template
- using lat/lon
- remove versions for reqs
- checking for !=0 instead of ==1
- added bool_false
- add boolean values
- removed astropy.Time
- workers for gunicorn
- re-organized folders
- not providing font sizes in css
- re-organized directories
- added fonts and moved static dir
- added title
- deleting Station also deletes PeriodicTask
- all weather stations now have common base class
- back to 5 min averages
- changed _add_value
- only active stations
- new base class
- two modes for monet station
- back to current, need to fix avg...
- new url for weather station
- moved script tags
- added missing file
- added sensors page
- fixed delay
- add skytemp to default values/plots
- sunset/sunrise
- overall good/bad
- added switch
- evaluation
- regular updates of plots and values
- time formatting
- adding offset instead of subtracting it...
- added time offset
- update only active stations
- use Time for time
- docker file
- new initials
- mysql station
- sql station
- added favicons
- plot style
- averages and plot
- styles
- all plots
- working on chart.js
- using Chart.js instead of plotly
- added files
- replacing plot.ly plots
- location as numbers
- added Observer station to initials
- observer
- added current/ to API
- navigation
- added basic API
- css
- logging
- cleaning up
- evaluating sensors
- added current values
- fixed crontab for average
- skip stations in plot and plot colors
- fixed bugs
- monet station
- averages
- McDLocke and Current are working again
- plots
- first plot
- started with frontend
- renamed app to "weather"
- delay works (?)
- >= instead of >
- setting Sensor.since when good changes
- evaluating works
- current and average work
- .
- json with initial values
- working on evaluators
- The "average" station is just a normal station
- average values
- periodic updates work
- periodic events working
- initial commit
