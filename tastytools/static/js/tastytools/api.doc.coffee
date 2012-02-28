dumpObjectIndented = (obj, indent="", isProp=false) ->

  isArray = obj instanceof Array
  isObject = typeof obj is "object" and not isArray
  isString = typeof obj is "string"
  isNumber = typeof obj is "number"
  isBoolean = typeof obj is "boolean"

  if isString
    out = '"' + obj + '"'
    if isProp
      return out
    else
      return indent + out
  if isNumber or isBoolean
    if isProp
      return obj
    else
      return indent + obj
  if isObject
    result = ""
    for own property, value of obj
      value = dumpObjectIndented(value, indent + "  ", true)
      result += indent + "'" + property + "' : " + value + ",\n"

    out = "{\n"
    out += result
    out += indent[2..]
    out += "}"
    if not isProp
      out = indent + out
  if isArray
    if obj.length is 0
      out = "[]"
    else if obj.length is 1
      out = "["+dumpObjectIndented(obj[0], indent + "  ", true)+"]"
    else
      ods = (dumpObjectIndented(item, indent + "  ")+"\n" for item in obj)
      out = "[ \n" + ods + "\n"+"]\n"

  out = out.replace(/\n,/g, ",\n")
  out = out.replace(/\n\n/g, "\n")
  return out


class ResourceFieldModel extends Backbone.Model


class ResourceFieldView extends Backbone.View

  initialize : (options) ->
    @template = _.template($("#resource_field_template").html())

  render : ->
    data = @model.toJSON()
    jqRendered = $(@template(data))

    for flag in ['nullable','readonly','unique','blank']
      selector = "span.flag_#{flag}"
      jqRendered.find(selector).toggleClass('active_flag', data[flag])

    $(@el).html jqRendered
    return this


class ResourceModel extends Backbone.Model
  initialize : (options) ->
    _.bindAll(@,'modelChange')
    @resourceName = options.resourceName
    @bind('change',@modelChange)
    super(options)

  modelChange : (args...) ->
    if @hasChanged("schema")
      @url = @get('schema')
      @fetch()
      @url = @get("list_endpoint")+"example/"
      @fetch
        error : =>
          @set(POST : false)
          @set(GET : false)

    @fields = []
    for fieldName, fieldData of @toJSON().fields
      fieldData.default_value = fieldData.default
      fieldData.name = fieldName
      @fields.push new ResourceFieldModel(fieldData)

  loaded : ->
    return  @.toJSON()['fields'] isnt undefined

class ResourceView extends Backbone.View
  el: "#resource"

  initialize : (options) ->
    _.bindAll(@, 'render')
    @model or= new ResourceModel()
    @model.bind('change',@render)
    @template = _.template($("#resource_template").html())


  formatExampleData : (method, data) ->
    METHOD = method.toUpperCase()
    method = method.toLowerCase()

    allowed_methods = data.allowed_detail_http_methods.concat data.allowed_list_http_methods
    method_is_allowed = method in allowed_methods
    method_has_data = data[METHOD]

    if method_is_allowed and method_has_data
      data[METHOD] = dumpObjectIndented data[METHOD]
    else
      data[METHOD] = "// not allowed"

  #highlightIfAllowed : (data, action, method) ->
  #  selector = ".#{action}_methods .#{method}_method"
  #  allowed_methods = data["allowed_#{action}_http_methods"]
  #  $(@el).find(selector).toggleClass('allowed', method in allowed_methods)

  render : ->
    $(@el).empty()
    if not @model or not @model.loaded()
      return this

    data = @model.toJSON()
    data.resource_name = @model.resourceName

    @formatExampleData('POST', data)
    @formatExampleData('GET', data)

    $(@el).html(@template(data))
    jqFieldsList = $(@el).find('.fields_list')

    for field in @model.fields
      fieldView = new ResourceFieldView(model: field)
      fieldView.render()
      jqFieldsList.append($(fieldView.el).html())

    SyntaxHighlighter.highlight()
    return this


class ResourceList extends Backbone.Model
  url : ()->
      return window.api_url


class ResourceListView extends Backbone.View
  el: "#resource_list"

  initialize: ->
    _.bindAll(@,'render')
    @model.bind('change',@render)
    @resTemplate = _.template($("#resources_btn_template").html())
    @currentModel = false
    @currentModelView = new ResourceView()

  render : ->
    $(@el).empty()
    for resourceName, resourceProps of @model.toJSON()
      tmpl_data = resource_name : resourceName
      jqBtn = $(@resTemplate(tmpl_data))
      do (resourceName, resourceProps) =>
        jqBtn.click =>
          @currentModelView.model.set resourceProps
          @currentModelView.model.resourceName = resourceName
      $(@el).append(jqBtn)

    @currentModelView.render()

$(document).ready ->
  resources = new ResourceList()
  resourcesView = new ResourceListView(model:resources)
  resources.fetch()
  window.resourcesView = resourcesView
