"""
 	@author
        Zhibin Gou
 		Email: zebgou@gmail.com
 		Github: https://github.com/ZubinGou

	@license
		MIT License
		Copyright (c) 2023. Anonymous authors. All rights reserved
        Do not distribute.
"""

from web_tools.core import engines
from web_tools.core.engines.aol import Search as AolSearch
from web_tools.core.engines.ask import Search as AskSearch
from web_tools.core.engines.baidu import Search as BaiduSearch
from web_tools.core.engines.bing import Search as BingSearch
from web_tools.core.engines.github import Search as GithubSearch
from web_tools.core.engines.google import Search as GoogleSearch
from web_tools.core.engines.googlescholar import \
    Search as GoogleScholarSearch
from web_tools.core.engines.stackoverflow import \
    Search as StackOverflowSearch

name = "llm-agent-web-tools"  # pylint: disable=invalid-name
__version__ = "0.2.1"
