
utils = window.utils =
    nonUniqueIndexBy : (data, prop) ->
        propFn = if typeof prop is "function" then prop else (o) -> o[prop]

        result = {}

        for element in data
            value = propFn(element)
            if value
                if result.hasOwnProperty(value)
                    result[value].push(element)
                else
                    result[value] = [element]
        result

    leftPad : (value, size, pad) ->
        value = value.toString()
        while value.length < size
            value = pad + value
        value

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec']

leftPad = utils.leftPad

dates = window.dates =
    MS_IN_DAY : (1000 * 60 * 60 * 24)

    today: ->
        return dates.truncate(new Date())

    truncate:(date) ->
        return new Date(Math.floor(date.getTime() / dates.MS_IN_DAY) * dates.MS_IN_DAY)

    addDay:(date, delta) ->
        return new Date( date.getTime() + (dates.MS_IN_DAY * delta))

    formatY8:(d) ->
        if d
            return d.getUTCFullYear() + '-' + leftPad(d.getUTCMonth()+1, 2,'0') + '-' + leftPad(d.getUTCDate(), 2, '0')
        return null

    formatDateTime:(value) ->
        if typeof value is 'string'
            value = dates.parse(value);

        return "#{value.getUTCDate()} #{months[value.getUTCMonth()]} #{leftPad(value.getUTCHours(),2,'0')}:#{leftPad(value.getUTCMinutes(),2,'0')}"

    parse:(input) ->
        return null if input == null

        if input.length == 10 or input.length == 19
            d = dates.today()
            d.setUTCFullYear(parseInt(input.slice(0,4),10))
            d.setUTCMonth( -1 + parseInt(input.slice(5,7),10) )
            d.setUTCDate(parseInt(input.slice(8,10),10))
            if input.length == 19
                d.setUTCHours(parseInt(input.slice(11,13)))
                d.setUTCMinutes(parseInt(input.slice(14,16)))
                d.setUTCSeconds(parseInt(input.slice(17,19)))
            return d

        throw new Error("parse exception")























