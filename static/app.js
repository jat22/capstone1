
const $searchParams = $('#search-params')

const $activitySelector = $('#activities')
const $facilitiesSelector = $('#facilities')
const $campgroundSelector = $('#campgrounds')
const $cityStateSelector = $('#city-state')
const $zipSelector = $('#zip')
const $resultsList = $('#results-list')

const $searchBtn = $('#search-btn')

function toggle_search_type(){
	if($cityStateSelector.is(' :checked')){
		$("#city-field").show();
		$("#state-field").show();
		$("#zip-field").hide().val("")
	}
	if($zipSelector.is(' :checked')){
		$("#city-field").hide().val("");
		$("#state-field").hide().val("");
		$("#zip-field").show()
	}
}

$searchParams.on('click', toggle_search_type)


async function do_search(evt){
	evt.preventDefault();
	$resultsList.empty();
	search_type = $("input[name='search-type']:checked").val()
	const resp = await axios.get('/api/search', {
		params : {
			search_type : search_type,
			location_type : $("input[name='location-type']:checked").val(),
			city : $('#city-field').val(),
			state : $('#state-field').val(),
			zip : $('#zip-field').val()
		}
	})
	results = resp.data;

	console.log(results)
	render_search_results(results, search_type)
}

$searchBtn.on('click', do_search)



function render_search_results(results, search_type){
	if(search_type == "activities"){

	}
	
	results.forEach(result =>
		$resultsList.append( 
			`<li class="list-group-item" id=${result.id}>${result.id}</li>`)
		)
	
}

