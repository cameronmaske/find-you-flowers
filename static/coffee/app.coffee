###
Declare the app. A global level module where you can create routes, models, etc.
[] is where you list any other modules for dependency injection.
###
app = angular.module('flowerApp', ['ui.bootstrap'])

# Configure angular to evaluate square brackets for interpolation.
# In simpler terms, you now use [[ variable ]] instead of {{ variable }}
# This avoids confilcts with jinja.
app.config(($interpolateProvider) ->
    $interpolateProvider.startSymbol('[[')
    $interpolateProvider.endSymbol(']]')
)


app.config(($locationProvider, $routeProvider) ->
    $locationProvider.html5Mode(true);
    $routeProvider
        .when('/',
            controller: 'indexCtrl',
            )
        .otherwise(
            redirectTo: '/',
            )
)
###
Controllers.
Should contain only business logic.
DOM manipulation—the presentation logic of an application—is well known for
being hard to test. Putting any presentation logic into controllers
significantly affects testability of the business logic
###


app.controller('indexCtrl', ($scope, $location, $http) ->
    # Sort by default to the best matches.
    $scope.sort = '-__weight'

    # Update the query from the URL.
    $scope.query = $location.hash().replace('-', ' ')

    # When the query is updated, update the URL.
    $scope.$watch 'query', (query) ->
        $location.hash(query.replace(' ', '-'))

    # Get all flowers possible.
    $http.get('/all/').then (response) ->
        $scope.flowers = response['data']['results']

    # Get search suggestion.e
    $http.get('/suggested/').then (response) ->
        $scope.suggested = response['data']['results']

)


app.filter('truncate', ->
    (text, length) ->
        if text.length > length then text.substring(0, length) + "..." else text
    )

app.filter('search', ->
    (array, query, fields) ->
        console.time("Search")
        if array
            for each in array
                score = 0
                for key of fields
                    weight = fields[key]
                    if each[key].toLowerCase().indexOf(query) > -1
                        score += weight
                each['__weight'] = score
            results = _.sortBy(_.filter(array, (item) -> item['__weight'] > 0), (item) -> -item['__weight'])
        console.timeEnd("Search")
        return results
    )


