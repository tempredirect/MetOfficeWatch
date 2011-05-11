buildFiveDayDates = (from)->
    today = dates.parse(from)
    for i in [0..4]
        dates.formatY8 dates.addDay(today, -i)


#http://www.metoffice.gov.uk/public/pws/invent/lib/images/wxsymbols/w12BIG.gif

window.showSiteDialog = (site) ->
    $dialog = $('#site-dialog')
                .tmpl(site)
                .appendTo(document.body)
                .overlay({
                           mask:{
                               color:'#333',
                               loadSpeed:200,
                               opacity:0.8
                           },
                           load:true})


    $.getJSON("/sites/#{site.id}/detail", (data) ->
        $tbody = $dialog.find('table.weather tbody')
        forecasts = utils.nonUniqueIndexBy(data.forecasts, 'forecast_datetime')

        for obs in data.observations
            datetime = obs.observation_datetime
            forecastsList = forecasts[datetime]
            today = dates.today()

            obs.best_forecasts = if forecastsList
                    forecastsByIssueDate = utils.nonUniqueIndexBy(forecastsList, (f) -> f.issued_datetime.slice(0,10))
                    fiveDayDates = buildFiveDayDates(obs.observation_date)
                    obs.best_forecasts = for d in fiveDayDates
                        f = forecastsByIssueDate[d]
                        if f then _.first(f) else null

                else
                    # no forecasts just return null in all the slots
                    null for i in [0..4]

        $tbody.children().remove()
        $('#site-observations-rows')
            .tmpl(data.observations, format: dates.formatDateTime )
            .appendTo($tbody)
    )
