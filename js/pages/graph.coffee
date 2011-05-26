
@loadSiteGraph = (site,target) ->
    $.getJSON "/sites/#{site}/series", (data) ->
        parseDate = dates.parse
        options = chart:
                renderTo: 'graph_canvas'
                defaultSeriesType: 'spline'
                marginRight: 130
                marginBottom: 50
            title:
                text: 'Daily temperatures'
                x: -20
            subtitle:
                text: 'Source: metoffice.gov.uk'
                x: -20
            xAxis:
                type:'datetime'
            yAxis:
                title:
                    text: 'Temperature (¡C)'
                min:0
#            plotLines: [{
#                value: 0,
#                width: 1,
#                color: '#808080'
#            }]
            series: for s in data.series
                {
                    name: s.name
                    data: for i in s.data.reverse()
                        [parseDate(i[0]).getTime(), i[1]]
                }
        chart = new Highcharts.Chart options
