
$(function(){
  // const flatpickr = require("flatpickr");

  var textareaCountMax = 117;
  $("[name=invite_message]").bind('keydown keyup keypress change',function(){
      var thisValueLength = $(this).val().length;
      var countDown = (textareaCountMax)-(thisValueLength);

      if(countDown < 0){
          $(this).css({background:'#ffcccc'});
      } else {
          $(this).css({background:'#ffffff'});
      }
  });

});
