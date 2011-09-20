$(function(){
		var addlist = {
			add: function(name){
				$el = $($('#'+name+'-tpl').html()).appendTo('#questions-wrap').find('input.section-name').focus().end();
				addlist.setup_tools($el);
			},
			setup_adder: function(item){
				var ghost = item.find('.ghost'), tpl = $($('#question-tpl').html());
				ghost.bind('click focus',function(){
					$(this).before(tpl);
					$(this).prev().focus();
				});
			},
			setup_tools: function(el){
				var tools = el.append($('#tools-tpl').html());
				tools.find('.del').click(function(){
					el.remove();
				}).end().find('up').click(function(){
					//pass
				}).end().find('down').click(function(){
					//pass
				});
			}
		};
		!function(){
			var sess = document.cookie.match('session_key=([^&]+)');
			if (sess && sess[1]){
				$.getScript('https://graph.facebook.com/me?callback=login_check&access_token='+sess[1]);
			}
			window.oauth = false;
			window.login_check = function(data){
				if (data['error']){
					window.oauth = false;
				} else if (data['id']){
					window.oauth = true;
				}
			}
		}();
		window.runlogin = function(){
			var sess = document.cookie.match('session_key=([^&]+)');
			if (sess && window.oauth){
				return true;
			} else {
				var popwin = window.open('/fb/connect');
				return false;
			}
		}
		var triggers = {
			'#create-yes-no .questions-wrap':function(){
			    var tpl = this.html();
			    this.children().remove();
				for(var num = 0; num < 5;num++){
					this.append(tpl.replace(/#/g,num));
					var questions = this.find('#quest-'+num+' ul.questions'),
					    question = questions.html();
					for (var box = 0; box < 5; box++){
						questions.append(question);
					}
				}
				this.find('input:eq(0)').focus();
			},
			'.choices li': function(){
				$('ul.choices a').click(function(){
					addlist.add($(this).attr('id').substr(2));
					return false;
				});
				var clone =  function(){$($('#question-tpl').html()).insertBefore($(this).parents('.ghost')).find('input').focus();};
				$('.ghost').live('focus', clone);
				$('.ghost .add').live('click', clone);
			},
			'.go-sub': function(){
				this.click(function(){ 
						if (runlogin()){ sendChoices(); }
						return false; });
			},
			'#take-note': function(){
				window.login_evt = function(){
				window.oauth= true;
    				$('#take-note').submit();
    			}
  			    $('#take-note').submit(runlogin);
			},
			'#create-note': function(){
				window.login_evt = function(){
					//$('#create-note').submit();
					sendChoices();
				};
				$('#create-note .go-sub').click(runlogin);
			},
			'': function(){
				'http://ws.audioscrobbler.com/2.0/?method=track.search&format=json&callback=sugg_go&track=boo&autocorrect=true&limit=5&api_key=b25b959554ed76058ac220b7b2e0a026' //autocomplete url
			}
		};
		for (trigger in triggers){
		    var el = $(trigger);
			if (trigger.length > 0 && el.length > 0){
				triggers[trigger].call(el);
			}
		}
});
	function sendChoices(){
			if (typeof(JSON) == 'undefined'){ $.getScript('/assets/scripts/json2.min.js', function(){ sendChoices(); }); }
			var results = [];
			$('#questions-wrap .section').each(function(){
				var header = $(this).find('input.section-name').val();
				if (header.length == 0){ alert('please provide a header!'); return false; }
				var section = {type: $(this).attr('type'), questions:[], text: header};
				$(this).find('input.question:not(.ghost)').each(function(){
					if (this.value != ''){
						section.questions.push(this.value);
					} else { $(this).parent().remove(); }
				});
				results.push(section);
			});
			if ($('#note-name').val().length == 0){ alert('Please Entitle your Note!'); return false; }
			$.post('/submit', {data: JSON.stringify({sections: results, 'name': $('#note-name').val()})}, function(result){
				if (result.success){
					alert('Note '+result.name+' created!');
					window.location = '/note/' + result.permalink
				} else {
					alert('Chute! Something went wrong: ('+ result.error +')');
				}
				alert(result);
			}, 'json');
			return false;
		}

