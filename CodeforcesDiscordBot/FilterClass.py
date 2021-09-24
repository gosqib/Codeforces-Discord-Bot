from RandomClass import *



"""create dictionary and store the entire url code + space PLUS the comma for easy finding"""
class FilterProblem:
    def __init__(self, lower_bound: int, upper_bound: int, *tags) -> None:
        self._MIN_RATING = lower_bound
        self._MAX_RATING = upper_bound
        self._FILTERED_TAGS = [*tags]
        
        self._TAGS_TO_URL = {
            '2-sat'                     : "2-sat,",
            'binary-search'             : "binary%20search,",
            'bitmasks'                  : "bitmasks,",
            'brute-force'               : "brute%20force,",
            'chinese-remainder-theorem' : "chinese%20remainder%20theorem,",
            'combinatorics'             : "combinatorics,",
            'constructive-algorithms'   : "constructive%20algorithms,",
            'data-structures'           : "data%20structures,",
            'dfs-and-similar'           : "dfs%20and%20similar,",
            'divide-and-conquer'        : "divide%20and%20conquer,",
            'dp'                        : "dp,",
            'dsu'                       : "dsu,",
            'expression-parsing'        : "expression%20parsing,",
            'fft'                       : "fft,",
            'flows'                     : "flows,",
            'games'                     : "games,",
            'geometry'                  : "geometry,",
            'graph-matchings'           : "graph%20matchings,",
            'graphs'                    : "graphs,",
            'greedy'                    : "greedy,",
            'hashing'                   : "hashing,",
            'implementation'            : "implementation,",
            'interactive'               : "interactive,",
            'math'                      : "math,",
            'matrices'                  : "matrices,",
            'meet-in-the-middle'        : "meet-in-the-middle,",
            'number-theory'             : "number%20theory,",
            'probabilities'             : "probabilities,",
            'schedules'                 : "schedules,",
            'shortest-paths'            : "shortest%20paths,",
            'sortings'                  : "sortings,",
            'string-suffix-structures'  : "string%20suffix%20structures,",
            'strings'                   : "strings,",
            'ternary-search'            : "ternary%20search,",
            'trees'                     : "trees,",
            'two-pointers'              : "two%20pointers,",
        }

        self._WEBSITE = "https://codeforces.com/problemset?tags="


    def build_link(self):
        """create the sendable link using the filters"""

        for tag in self._FILTERED_TAGS:
            if tag in self._TAGS_TO_URL:
                self._WEBSITE += self._TAGS_TO_URL[tag]
        return f"{self._WEBSITE}{self._MIN_RATING}-{self._MAX_RATING}"


    def to_link(tag: str) -> str:
        if tag in ('meet-in-the-middle', '2-sat'):
            return tag + ','

        return tag.replace('-', '%20') + ','


