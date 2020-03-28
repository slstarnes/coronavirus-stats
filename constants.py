# JHU_DATA = 'https://raw.githubusercontent.com/CSSEGISandData/' \
#            'COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/' \
#            'time_series_covid19_confirmed_global.csv'

# https://www.soothsawyer.com/john-hopkins-time-series-data-confirmed-case-csv-after-march-22-2020/
JHU_DATA = 'https://www.soothsawyer.com/wp-content/uploads/' \
           '2020/03/time_series_19-covid-Confirmed.csv'

JHU_DEATH_DATA = 'https://www.soothsawyer.com/wp-content/uploads/2020/03/' \
                 'time_series_19-covid-Deaths.csv'

NYT_STATE_DATA = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'

# this is the URL to the CSV file in GitHub so you can parse date of last commit.
# (the REST API required auth)
JHU_DATA_FILE_URL = 'https://github.com/CSSEGISandData/COVID-19/blob/master/' \
                     'csse_covid_19_data/csse_covid_19_time_series/' \
                     'time_series_covid19_confirmed_global.csv'
NYT_STATE_DATA_FILE_URL = 'https://github.com/nytimes/covid-19-data/blob/master/us-states.csv'

COUNTRY_T0_CASES_THRESHOLD = 100
STATE_T0_CASES_THRESHOLD = 1
COUNTRY_T0_DEATHS_THRESHOLD = 10
STATE_T0_DEATHS_THRESHOLD = 1
CASES_PER_CAPITA_VALUE = 100_000
DEATHS_PER_CAPITA_VALUE = 1_000_000
PLOT_LOOKAHEAD = 7  # days
TRACE_COLORS = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B3",
                "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD"]
