import sublime, sublime_plugin
import re
from .completions import completion_tags
from .attributes import global_attributes
from .dictionary import tag_dict
from .tags import normal_tags

def match(rex, str):
    m = rex.match(str)
    if m:
        return m.group(0)
    else:
        return None


# 创建元素自动完成
def make_cola_completion(tag):
    return (tag + '\tTag', tag + '>$0</' + tag + '>')


# 获得Cola 标签的Attributes
def get_cola_tag_to_attributes():
    for attributes in tag_dict.values():
        attributes.extend(global_attributes)

    if 'bdi' in tag_dict:
        tag_dict['bdi'] = [attr for attr in tag_dict['bdi'] if attr != 'dir']

    return tag_dict


class ColaCompletions(sublime_plugin.EventListener):
    def __init__(self):
        completion_list = self.default_completion_list()
        self.prefix_completion_dict = {}
        for s in completion_list:
            prefix = s[0][0]
            self.prefix_completion_dict.setdefault(prefix, []).append(s)

        self.tag_to_attributes = get_cola_tag_to_attributes()

    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "text.html - source - string.quoted"):
            return []

        is_inside_tag = view.match_selector(locations[0],
                                            "text.html meta.tag - text.html punctuation.definition.tag.begin")

        return self.get_completions(view, prefix, locations, is_inside_tag)

    def get_completions(self, view, prefix, locations, is_inside_tag):
        if not is_inside_tag:
            tag_attr_expr = self.expand_tag_attributes(view, locations)
            if tag_attr_expr != []:
                return (tag_attr_expr, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        pt = locations[0] - len(prefix) - 1
        ch = view.substr(sublime.Region(pt, pt + 1))

        completion_list = []
        if is_inside_tag and ch != '<':
            if ch in [' ', '\t', '\n']:
                completion_list = self.get_attribute_completions(view, locations[0], prefix)
            return (completion_list, sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        if prefix == '':
            return ([], sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS)

        completion_list = self.prefix_completion_dict.get(prefix[0], [])

        if ch != '<':
            completion_list = [(pair[0], '<' + pair[1]) for pair in completion_list]

        flags = 0
        if is_inside_tag:
            flags = sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS

        return (completion_list, flags)

    def default_completion_list(self):
        default_list = []

        for tag in normal_tags:
            default_list.append(make_cola_completion(tag))
            default_list.append(make_cola_completion(tag.upper()))

        default_list += completion_tags

        return default_list

    def expand_tag_attributes(self, view, locations):
        lines = [view.substr(sublime.Region(view.line(l).a, l))
                 for l in locations]

        lines = [l[::-1] for l in lines]

        rex = re.compile("([\w-]+)([.#])(\w+)")
        expr = match(rex, lines[0])
        if not expr:
            return []

        for i in range(1, len(lines)):
            ex = match(rex, lines[i])
            if ex != expr:
                return []

        arg, op, tag = rex.match(expr).groups()

        arg = arg[::-1]
        tag = tag[::-1]
        expr = expr[::-1]

        if op == '.':
            snippet = '<{0} class=\"{1}\">$1</{0}>$0'.format(tag, arg)
        else:
            snippet = '<{0} id=\"{1}\">$1</{0}>$0'.format(tag, arg)

        return [(expr, snippet)]

    def get_attribute_completions(self, view, pt, prefix):
        SEARCH_LIMIT = 500
        search_start = max(0, pt - SEARCH_LIMIT - len(prefix))
        line = view.substr(sublime.Region(search_start, pt + SEARCH_LIMIT))

        line_head = line[0:pt - search_start]
        line_tail = line[pt - search_start:]

        i = len(line_head) - 1
        tag = None
        space_index = len(line_head)
        while i >= 0:
            c = line_head[i]
            if c == '<':
                tag = line_head[i + 1:space_index]
                break
            elif c == ' ':
                space_index = i
            i -= 1
        if not tag:
            return []

        suffix = '>'

        for c in line_tail:
            if c == '>':
                suffix = ''
                break
            elif c == '<':
                break

        if suffix == '' and not line_tail.startswith(' ') and not line_tail.startswith('>'):
            suffix = ' '

        attributes = self.tag_to_attributes.get(tag, [])
        attri_completions = [(a + '\tAttr', a + '="$1"' + suffix) for a in attributes]
        return attri_completions
