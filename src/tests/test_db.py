# import pytest
# from src.vkbot.db.data_classes import DataClassesDBI
# from src.vkbot.db.db_interface import DatabaseInterface
# from src.tests.fixtures_preparation import fixtures_good, fixtures_preparation
# from src.config import DatabaseConfig
#
#
# FIXTURES = [(fixtures_preparation(**fixtures_good()), [True, True, True, True, True])]
#
#
# def setup_function():
#     dbc = DatabaseConfig()
#     DataClassesDBI.dbi = DatabaseInterface(dbc)
#
#
# def teardown_function():
#     for fixture in FIXTURES:
#         for target in fixture[0].targets:
#             target.remove_favorite(client_vk_id=fixture[0].client_vk_id)
#
#
# @pytest.mark.parametrize('targets, expected_results', FIXTURES)
# def test_target_add_favorite(targets, expected_results):
#     results = []
#     for target in targets.targets:
#         result = target.add_favorite(targets.client_vk_id)
#         results.append(result)
#     assert results == expected_results
