"""Tool schemas — what the LLM sees."""

ZIM_LIST_PAGES = {
    "name": "zim_list_pages",
    "description": (
        "List pages in a Zim Desktop Wiki notebook using the Zim index. "
        "Returns page names (colon notation) and metadata. Use to discover "
        "notebook structure before reading or editing."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "prefix": {
                "type": "string",
                "description": (
                    "Optional namespace prefix to limit results "
                    "(e.g. 'Notes' or 'Projects:Dev'). Empty means entire notebook."
                ),
            },
        },
        "required": [],
    },
}

ZIM_READ_PAGE = {
    "name": "zim_read_page",
    "description": (
        "Read a Zim wiki page by name (e.g. 'Home' or 'Notes:My Page'). "
        "Returns wiki markup body via the Zim parser. Use before editing."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "page": {
                "type": "string",
                "description": "Page name in Zim colon notation (Section:Page Name)",
            },
        },
        "required": ["page"],
    },
}

ZIM_SEARCH = {
    "name": "zim_search",
    "description": (
        "Search Zim wiki pages using Zim's query language. Plain text searches "
        "content and names. Keywords: Content:, Name:, Tag:, LinksFrom:, "
        "LinksTo:, Section:. Operators: AND, OR, NOT (or -). Examples: "
        "'meeting notes', 'Tag:todo', 'LinksTo:Home', 'Content:python AND Tag:work'."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Zim search query string",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results to return (default 20)",
            },
        },
        "required": ["query"],
    },
}

ZIM_WRITE_PAGE = {
    "name": "zim_write_page",
    "description": (
        "Replace the body of an existing Zim wiki page. Content is parsed and "
        "stored via the Zim API (correct headers and line endings). Does not "
        "create new pages. Read the page first with zim_read_page."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "page": {
                "type": "string",
                "description": "Page name in Zim colon notation",
            },
            "body": {
                "type": "string",
                "description": "New page body as Zim wiki markup",
            },
        },
        "required": ["page", "body"],
    },
}

ZIM_GET_LINKS = {
    "name": "zim_get_links",
    "description": (
        "List links to or from a Zim page using the notebook index. "
        "Use backward for backlinks (what links here), forward for outbound links."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "page": {
                "type": "string",
                "description": "Page name in Zim colon notation",
            },
            "direction": {
                "type": "string",
                "description": "forward, backward, or both (default both)",
                "enum": ["forward", "backward", "both"],
            },
        },
        "required": ["page"],
    },
}

ZIM_LIST_TAGS = {
    "name": "zim_list_tags",
    "description": (
        "List tags in the notebook. Provide page to list tags on that page, "
        "or tag to list pages with that tag. If neither is given, lists all tags."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "page": {
                "type": "string",
                "description": "Page name — list tags used on this page",
            },
            "tag": {
                "type": "string",
                "description": "Tag name (with or without @) — list pages with this tag",
            },
        },
        "required": [],
    },
}

ZIM_CREATE_PAGE = {
    "name": "zim_create_page",
    "description": (
        "Create a new Zim wiki page or append to an existing one. Uses the Zim "
        "API to parse and store wiki markup with correct format. Fails if the "
        "page exists unless append is true."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "page": {
                "type": "string",
                "description": "Page name in Zim colon notation",
            },
            "body": {
                "type": "string",
                "description": "Page body as Zim wiki markup",
            },
            "append": {
                "type": "boolean",
                "description": "If true, append body to an existing page (default false)",
            },
        },
        "required": ["page", "body"],
    },
}
