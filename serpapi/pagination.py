import pprint
from loguru import logger

DEFAULT_START = 0
DEFAULT_END = 1000000000
DEFAULT_num = 10

# Paginate response in SearpApi
class Pagination:
    def __init__(self, client, start=DEFAULT_START, end=DEFAULT_END, num=DEFAULT_num):
        # serp api client
        self.client = client
        # range
        self.start = start
        self.end = end
        self.num = num

        # use value from the client
        if self.start == DEFAULT_START:
            if "start" in self.client.params_dict:
                self.start = self.client.params_dict["start"]
        if self.end == DEFAULT_END:
            if "end" in self.client.params_dict:
                self.end = self.client.params_dict["end"]
        if self.num == DEFAULT_num:
            if "num" in self.client.params_dict:
                self.num = self.client.params_dict["num"]

        # basic check
        if self.start > self.end:
            raise ValueError(
                "start: {} must be less than end: {}".format(self.start, self.end)
            )
        if (self.start + self.num) > self.end:
            raise ValueError(
                "start + num: {} + {} must be less than end: {}".format(
                    self.start, self.num, self.end
                )
            )

    def __iter__(self):
        logger.debug(
            f"Initialise pagination from __iter__ with {self.start =}, {self.end =}, {self.num =}"
        )
        self.update()
        return self

    def update(self):
        self.client.params_dict["start"] = self.start
        self.client.params_dict["num"] = self.num
        # if self.start > 0:
        #     self.client.params_dict["start"] += 1
        logger.debug(
            f"after running update() {self.start =}, {self.end =}, {self.num =}"
        )
        logger.debug(f'after running update() {self.client.params_dict["start"] =}')

    def __next__(self):
        # update parameter
        logger.debug("Calling update() from __next__()")
        self.update()

        # execute request
        result = self.client.get_dict()
        logger.debug("getting result from serpapi")
        logger.debug(f"\n\n\n\n\n\nresults:\n {result}\n\n\n\n\n\n")

        # # stop if backend miss to return serpapi_pagination
        # if not "serpapi_pagination" in result:
        #     logger.debug("Stopped as serpapi_pagination not present in results")
        #     raise StopIteration

        # # stop if no next page
        # if not "next" in result["serpapi_pagination"]:
        #     logger.debug('Stopped as next not found in result["serpapi_pagination"]')
        #     raise StopIteration

        # stop if no results for query
        if not "organic_results" in result:
            logger.debug("Stopped as no organic_results returned")
            raise StopIteration

        # ends if no next page
        if self.start + self.num > self.end:
            logger.debug("Stopped as start + page_size is now bigger than end")
            raise StopIteration

        # increment start page
        self.start += self.num
        logger.debug(f"incrementing start page: {self.start =}")

        return result
