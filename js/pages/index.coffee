buildFiveDayDates = (from)->
    today = dates.parse(from)
    return _([0..4]).chain()
        .map((i) -> dates.addDay(today, -i))
        .map(dates.formatY8)
        .value()


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

    $.getJSON('/sites/' + site.id + "/latest", (data) ->
        $tbody = $dialog.find('table.weather tbody')
        forecasts = utils.nonUniqueIndexBy(data.forecasts, 'forecast_datetime')

        for obs in data.observations
            datetime = obs.observation_datetime
            forecastsList = forecasts[datetime]
            today = dates.today()

            obs.best_forecasts = if forecastsList
                    forecastsByIssueDate = utils.nonUniqueIndexBy(forecastsList, (f) -> f.issued_datetime.slice(0,10))
                    fiveDayDates = buildFiveDayDates(obs.observation_date)
                    obs.best_forecasts = _.map(fiveDayDates, (d) ->
                        f = forecastsByIssueDate[d]
                        if f then _.first(f) else null
                    )
                else
                    # no forecasts just return null in all the slots
                    null for i in [0..4]

        $tbody.children().remove()
        $('#site-observations-rows')
            .tmpl(data.observations, { format: dates.formatDateTime })
            .appendTo($tbody)
    )
