/* Author: 

*/
$(function(){
  function leftPad(value, size, pad){
    value = value.toString();
    while( value.length < size ){
      value = pad + value;
    }
    return value;
  }

  var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec'];
  var dates = window.dates = {
    MS_IN_DAY : (1000 * 60 * 60 * 24),

    today:function(){
      return dates.truncate(new Date());
    },
    truncate:function(date){
      return new Date(Math.floor(date.getTime() / dates.MS_IN_DAY) * dates.MS_IN_DAY);
    },
    addDay:function( date, delta){
      return new Date( date.getTime() + (dates.MS_IN_DAY * delta));
    },
    formatY8:function(d){
      if(d){
        return d.getUTCFullYear() + '-' + leftPad(d.getUTCMonth() +1, 2,'0') + '-' + leftPad(d.getUTCDate(), 2, '0');
      }
      return null;
    },
    formatDateTime:function(value){
//      log(value);
      if( typeof value === 'string'){
        value = dates.parse(value);
      }
      return "" + (value.getUTCDate() + 1) + " " + months[value.getUTCMonth()]
          + " " + leftPad(value.getUTCHours(),2,'0') + ":" + leftPad(value.getUTCMinutes(),2,'0');
    },
    parse:function(input){
      var d;
      if( input === null ){
        return null;
      }
      if( input.length === 10 || input.length === 19){
        d = dates.today();
        d.setUTCFullYear(parseInt(input.slice(0,4),10));
        d.setUTCMonth(parseInt(input.slice(5,7),10) -1);
        d.setUTCDate(parseInt(input.slice(8,10),10));
        if( input.length === 19){
          d.setUTCHours(parseInt(input.slice(11,13)))
          d.setUTCMinutes(parseInt(input.slice(14,16)))
          d.setUTCSeconds(parseInt(input.slice(17,19)))
        }
        return d;
      }
      throw new Error("parse exception");
    }
  }
});























