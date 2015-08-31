$(function(){
	function onFormSubmit(event){
		var data = $(event.target).serializeArray();
		var thesis = {};

		for(var i = 0; i<data.length ; i++){
			thesis[data[i].name] = data[i].value;
		}

		var thesis_create_api = '/api/thesis';

		$.post(thesis_create_api, thesis, function(response){
			// read response from server
			if (response.status = 'OK') {
				var thesis_list = response.data.year + ' ' + response.data.thesisTitle + ' - by ' + response.data.first_name + ' ' + response.data.last_name;
				$('.thesis-list').prepend('<li>' + thesis_list + '<br><a href=\"/thesis/delete/'+response.data.id+'\"><button type=\"submit\">DELETE</button></a>'+ '<a href=\"/thesis/edit/'+response.data.id+'\"><button type=\"submit\">EDIT</button></a>')
				$('input:text').val('');
				$('textarea[name=abstract]').val('');
				$('select[name=year]').val('2011');
				$('select[name=section]').val('1');
			} else {

			}
		});

		return false;
	}

	function onRegister(event){
		var data = $(event.target).serializeArray();
		var user = {};

		for(var i = 0; i<data.length ; i++){
			user[data[i].name] = data[i].value;
		}

		var user_create_api = '/register';

		$.post(user_create_api, user, function(response){
			// read response from server
			if (response.status = 'OK') {
				location.href = '/home';
			}
		});

		return false;
	}

	function loadThesis(){
		var thesis_list_api = '/api/thesis';
		$.get(thesis_list_api, {} , function(response) {
			console.log('.thesis-list', response)
			response.data.forEach(function(thesis){
				var thesis_list = thesis.year + ' ' + thesis.thesisTitle + ' - by ' + thesis.first_name + ' ' + thesis.last_name;
				$('.thesis-list').append('<li>' + thesis_list + '<br><a href=\"/thesis/delete/'+thesis.id+'\"><button type=\"submit\">DELETE</button></a>'+ '<a href=\"/thesis/edit/'+thesis.id+'\"><button type=\"submit\">EDIT</button></a>' + '</li>')
			});
		});
		//var user_list_api = '/register';

		// $.get(user_list_api, {} , function(response) {
		// 	console.log('.thesis-list', response)
		// 	response.data.forEach(function(user){
		// 		var user_list = user.first_name;
		// 		$('.thesis-list').append('<li>' + user_list)
		// 	});
		// });

	}
	
    $('.create-form').submit(onFormSubmit);
    $('.register-form').submit(onRegister);
    loadThesis();
});