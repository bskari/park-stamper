from parks.tests.test_base import FunctionalTestBase


class AllParksUnitTest(FunctionalTestBase):
    def test_smoke(self):

        def is_redirect_route(description):
            """Returns true if the page should redirect."""
            return description.path in set(('/log-out',))

        def is_xhr_route(description):
            """Returns True if the page should only be accesses through JS."""
            return 'json' in description.path
        
        def requires_parameters(description):
            """Returns True if the page requires special parameters in order to
            be rendered.
            """
            return '{' in description.pattern

        routes = self.test_app.app.routes_mapper.routes
        GET_request_descriptions = (
            description for description in routes.values()
            # Some static routes don't have predicates
            if len(description.predicates) > 0
            and 'GET' in description.predicates[0].val
            and not is_xhr_route(description)
            and not requires_parameters(description)
        )
        for description in GET_request_descriptions:
            if is_redirect_route(description):
                expected_response = 302
            else:
                expected_response = 200

            response = self.test_app.get(description.path)
            self.assertEqual(
                response.status_code,
                expected_response,
                'Expected {expected_response} for {path} but got {code}'.format(
                    expected_response=expected_response,
                    path=description.path,
                    code=response.status_code,
                )
            )
