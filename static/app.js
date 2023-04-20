
const $searchParams = $('#search-params')

const $activitySelector = $('#activities')
const $facilitiesSelector = $('#facilities')
const $campgroundSelector = $('#campgrounds')
const $cityStateSelector = $('#city-state')
const $zipSelector = $('#zip')
const $resultsList = $('#results-list')

const $searchBtn = $('#search-btn')

function toggleSearchType(){
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

$searchParams.on('click', toggleSearchType)



function showResourceDetails(evt){
	$("#search-box").hide();
	$("#results-container").hide();
	$("#results-list").empty()

	const resourceId = evt.target.id

	const resources = JSON.parse(results)

	const resource = resources.find( res => res.name === resourceId)
		
	resource.parents.forEach( res => 
		$("#results-list").append(
			`<li class='list-group-item' id='${res.id}'>
			<form action="/${res.type}/${res.id}">
			<button type="submit" class="btn btn-link">${res.name}</button>
			</form>
			</li>`
		)
	)
	$("#resources-back-btn").show()
	// $('#results-card').append("<button class='btn btn-secondary' id='resources-back-btn'>Back</button>")
	
	$("#results-container").show()
	
}

$('li').on('click', showResourceDetails)


function backToSearchResults(evt){
	evt.preventDefault();
	console.log('click')
	$("#results-container").hide();
	$("#results-list").empty()

	const resources = JSON.parse(results)
	
	resources.forEach( res => 
		$("#results-list").append(
			`<li class="list-group-item" id="${res.name}">
			${res.name}
			</li>`
		))
	$('li').on('click', showResourceDetails)
	$("#results-container").show()
}

$('#resources-back-btn').on('click', backToSearchResults)