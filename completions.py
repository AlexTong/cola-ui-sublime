completion_tags = ([
    ('template\tTag', 'template name=\"$1\">$0</template>'),
    ('c-button\tTag', 'c-button caption=\"$1\">$0</c-button>'),
    ('c-panel\tTag', 'c-panel>'
                     '\n\t<div class="content">$0<div>'
                     '\n</c-panel>'),
    ('c-tab\tTag', 'c-tab>'
                   '\n\t<nav class="tab-bar">'
                   '\n\t\t<ul class="tabs">'
                   '\n\t\t\t<li name="name1" c-widget="TabButton;"><span class="caption">$0</span></li>'
                   '\n\t\t</ul>'
                   '\n\t</nav>'
                   '\n\t<ul class="content">'
                   '\n\t\t<li name="name1"></li>'
                   '\n\t</ul>'
                   '\n</c-tab>'),
    ('c-input\tTag', 'c-input bind=\"$1\">$0</c-input>')
])
