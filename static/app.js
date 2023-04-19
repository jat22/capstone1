
const $searchParams = $('#search-params')

const $searchField = $('#search')
const $activitySelector = $('#activities')
const $facilitiesSelector = $('#facilities')
const $campgroundSelector = $('#campgrounds')
const $cityStateSelector = $('#city-state')
const $zipSelector = $('#zip')

const $searchBtn = $('#search-btn')

function toggle_search_type(){
	if($activitySelector.is(' :checked')){
		$searchField.attr('placeholder', "Search for Activities")
	}
	if($facilitiesSelector.is(' :checked')){
		$searchField.attr('placeholder', "Search for Parks or Facilities")
	}
	if($campgroundSelector.is(' :checked')){
		$searchField.attr('placeholder', "Search for Campgrounds")
	}
	if($cityStateSelector.is(' :checked')){
		$("#city-field").show();
		$("#state-field").show();
		$("#zip-field").hide()
	}
	if($zipSelector.is(' :checked')){
		$("#city-field").hide();
		$("#state-field").hide();
		$("#zip-field").show()
	}
}

$searchParams.on('click', toggle_search_type)


async function do_search(evt){
	evt.preventDefault();
	const resp = await axios.get('/api/search', {
		params : {
			search_type : $("input[name='search-type']:checked").val(),
			location_type : $("input[name='location-type']:checked").val(),
			city : $('#city-field').val(),
			state : $('#state-field').val(),
			zip : $('#zip-field').val()
		}
	})
	results = resp.data
	console.log(results)
	render_search_results(results)
}

$searchBtn.on('click', do_search)


function render_search_results(results){
	results.forEach(result =>
		$('#results-list').append( 
			`<li class="list-group-item">${result.name}</li>`)
		)
}