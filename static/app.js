
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

$(document).ready(function(){
	if(window.location.href.indexOf('http://127.0.0.1:5000/search') > -1){
		localStorage.removeItem("currResults")
		localStorage.setItem("currResults", results)
	}
	if(window.location.href.indexOf('http://127.0.0.1:5000/activity') > -1){
		currResults = JSON.parse(localStorage.getItem("currResults"))
		activity = currResults.find(act => act.id == activityID)
		activity.parents.forEach( res =>
			$("#details-list").append(
				`<li class='list-group-item' id='${res.id}'>
				<form action="/${res.type}/${res.id}">
				<button type="submit" class="btn btn-link">${res.name}</button>
				</form>
				</li>`)
		)
		localStorage.removeItem("currResults")
	}
})