| Bug | Test(s) that failed |
| --- | --- |
| 1 | test_create_artwork (failed); also errored via the created_artwork fixture:            test_create_artwork_is_saved, test_update_artwork, test_delete_artwork, test_create_duplicate, test_create_duplicate_ignores_case, test_update_same_title_and_artist_is_allowed |
| 2 | test_create_duplicate_ignores_case |
| 3 | test_update_same_title_and_artist_is_allowed |
| 4 | test_delete_artwork |
| 5 | test_filter_by_artist[lowercase-partial] |