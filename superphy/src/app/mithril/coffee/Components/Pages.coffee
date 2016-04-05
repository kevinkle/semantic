# coffeelint: disable=max_line_length

class Home extends ComponentTemplate
    @controller: (args) ->
        view: () ->
            m ".container", {id:'Home.get()-beta'},
                m(".row"
                    m(".well center-block"
                        m("p.text-center"
                            m("span.text-info beta-release", "Beta Release")
                            " Some features are still under development and may not be fully functional."
                        )
                     )
                )
                m(".row superphy-image"
                    m("img", {src:'images/superphy_logo_with_title.png'}),
                    m("p.superphy-image"
                        'NEXT-LEVEL PHYLOGENETIC AND
                        EPIDEMIOLOGICAL ANALYSIS OF PATHOGENS'
                    )
                )
                m(".row well"
                    m("p",'A user-friendly, integrated platform for the predictive genomic analyses of '
                        m("em", 'Escherichia coli')
                    )
                    m("p", 'Provides near real-time analyses of thousands of genomes using novel computational approaches.')
                    m("p", 'Generates results that are understandable and useful to a wide community of users.')
                )
                m(".row"
                    m("button.btn btn-danger btn-lg center-block", "INTRODUCTION")
                )
                m(".row text-center"
                    m("p", 'For more information or to discuss possible collaboration, please contact:'
                        m("p", m("ul", m("li", 'Dr. Vic Gannon: vic.gannon@phac-aspc.gc.ca')))
                    )
                )

class FooFoo
    @controller: (args) ->
        args.id = args.id || 0
        @not_saved = m.prop("")
        @saved = m.prop(localStorage.getItem("saved#{args.id}"))
        @onunload = () ->
            localStorage.setItem("saved#{args.id}", @saved())
        return @

    @view: (ctrl) ->
        m('.'
            m('hr')
            
            "Saved"
            m('input[type=text]', {
                oninput: m.withAttr('value', ctrl.saved)
                value: ctrl.saved()
            })
            "Not Saved"
            m('input[type=text]', {
                oninput: m.withAttr('value', ctrl.not_saved)
                value: ctrl.not_saved()
            })
        )
"""
Bar = (response) ->
    console.log(response)
    return {'data': response.bar}



class FooBar
    @controller: (args) ->
        @data = m.request(
            method: "GET",
            url: "http://#{location.hostname}:5000/example/bar"
            data: null
            datatype: 'json'
            type: Bar
        )
        return @
    @view: (ctrl) ->
        console.log(ctrl.data())
        m(".", ctrl.data().foo)
"""
"""
Data = () ->
    return m.request(
        method: "GET",
        url: "http://#{location.hostname}:5000/example/bar"
        data: null
        datatype: 'json'
        type: (response) ->
            console.log(response)
            return {'data': response.bar}
    )

class FooBar
    @controller: (args) ->
        @data = Data()
        return @
    @view: (ctrl) ->
        console.log(ctrl.data())
        m(".", ctrl.data().data)
"""

MetaData = (args) ->
    args = args || {}
    #at this point the data is static. At a later date we can add in
    #expire times, or a query to the server to ask if it should be updated.
    @data ?= m.prop(JSON.parse(localStorage.getItem("MetaData")))
    if @data() is null or args.reset is true
        @data = m.request(
            method: "POST",
            url: "http://#{location.hostname}:5000/data/meta"
            data: {}
            datatype: 'json',
            type: (response) ->
                data = {}
                data.headers = response.head.vars
                data.rows = []
                for binding, x in response.results.bindings
                    data.rows[x] = {}
                    for item in response.head.vars
                        try
                            data.rows[x][item] = binding[item]['value']
                        catch
                            data.rows[x][item] = ''
                data.date = new Date()
                return data
        )
        localStorage.setItem("MetaData", JSON.stringify(@data()))
    return @data

class GroupBrowseFirst10
    @controller: (args) ->
        @data = MetaData({reset: true})
        return @
    sort_table = (list, attribute = 'data-sort-by') ->
        { onclick: (e) ->
            item = e.target.getAttribute(attribute)
            if item
                first = list[0]
                list.sort (a, b) ->
                    if isNaN(parseFloat(a[item] * 1))
                        if isNaN(parseFloat(b[item] * 1))
                            if a[item] > b[item] then 1
                            else if b[item] > a[item] then -1
                            else 0
                        else -1
                    else if isNaN(parseFloat(b[item] * 1)) then 1
                    else if a[item] * 1 < b[item] * 1 then 1
                    else if b[item] * 1 < a[item] * 1 then -1
                    else 0
                if first == list[0]
                    list.reverse()
            return
        }


    @view: (ctrl) ->
        m(".Occlusion", [
            m("table", [
                m("tr", [
                    for header in ctrl.data().headers
                        m('th[data-sort-by=' + header + ']', sort_table(list = ctrl.data().rows) ,[header])
                ])
                for row, x in ctrl.data().rows[0 .. 9]
                    m('tr', [
                        for header in ctrl.data().headers
                            m('td', [row[header]])
                    ])
            ])
        ])


class GroupBrowse
    @controller: (args) ->
        @data = MetaData()
        """m.request(
            method: "POST",
            url: "http://#{location.hostname}:5000/data/meta"
            data: {}
            datatype: 'json',
            type: (response) ->
                data = {}
                data.headers = response.head.vars
                data.rows = []
                for binding, x in response.results.bindings
                    data.rows[x] = {}
                    for item in response.head.vars
                        try
                            data.rows[x][item] = binding[item]['value']
                        catch
                            data.rows[x][item] = ''
                #A typecast request still returns a prop object. @data being assigned in the controller means we access it wil ctrl.data()
                return data
        )"""
        @sort_table = (list, attribute = 'data-sort-by') ->
            { onclick: (e) ->
                item = e.target.getAttribute(attribute)
                if item
                    first = list[0]
                    list.sort (a, b) ->
                        if isNaN(parseFloat(a[item] * 1))
                            if isNaN(parseFloat(b[item] * 1))
                                if a[item] > b[item] then 1
                                else if b[item] > a[item] then -1
                                else 0
                            else -1
                        else if isNaN(parseFloat(b[item] * 1)) then 1
                        else if a[item] * 1 < b[item] * 1 then 1
                        else if b[item] * 1 < a[item] * 1 then -1
                        else 0
                    if first == list[0]
                        list.reverse()
                return
            }
        return @
    state = {pageY: 0, pageHeight: window.innerHeight}
    window.addEventListener("scroll", (e) ->
        state.pageY = Math.max(e.pageY || window.pageYOffset, 0)
        state.pageHeight = window.innerHeight
        m.redraw()
    )
    @view: (ctrl) ->
        pageY = state.pageY
        begin = pageY / 46 | 0
        end = begin + (state.pageHeight /46 | 0 + 10)
        offset = pageY % 46
        m(".Occlusion", {style: {height: ctrl.data().rows.length * 46 + "px", position: "relative", top: -offset + "px"}}, [
            m("table", {style: {top: state.pageY + "px"}}, [
                m("tr", [
                    for header in ctrl.data().headers
                        m('th[data-sort-by=' + header + ']', ctrl.sort_table(list = ctrl.data().rows) ,[header])
                ])
                for row, x in ctrl.data().rows[begin .. end] #when JSON.stringify(row).search(/Unknown/i) > -1
                    m('tr', [
                        for header in ctrl.data().headers
                            m('td', [row[header]])
                    ])
            ])
        ])