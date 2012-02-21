(function() {
  var ResourceFieldModel, ResourceFieldView, ResourceList, ResourceListView, ResourceModel, ResourceView, dumpObjectIndented;
  var __hasProp = Object.prototype.hasOwnProperty, __extends = function(child, parent) {
    for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; }
    function ctor() { this.constructor = child; }
    ctor.prototype = parent.prototype;
    child.prototype = new ctor;
    child.__super__ = parent.prototype;
    return child;
  }, __slice = Array.prototype.slice, __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; }, __indexOf = Array.prototype.indexOf || function(item) {
    for (var i = 0, l = this.length; i < l; i++) {
      if (this[i] === item) return i;
    }
    return -1;
  };
  dumpObjectIndented = function(obj, indent, isProp) {
    var isArray, isBoolean, isNumber, isObject, isString, item, ods, out, property, result, value;
    if (indent == null) {
      indent = "";
    }
    if (isProp == null) {
      isProp = false;
    }
    isArray = obj instanceof Array;
    isObject = typeof obj === "object" && !isArray;
    isString = typeof obj === "string";
    isNumber = typeof obj === "number";
    isBoolean = typeof obj === "boolean";
    if (isString) {
      out = '"' + obj + '"';
      if (isProp) {
        return out;
      } else {
        return indent + out;
      }
    }
    if (isNumber || isBoolean) {
      if (isProp) {
        return obj;
      } else {
        return indent + obj;
      }
    }
    if (isObject) {
      result = "";
      for (property in obj) {
        if (!__hasProp.call(obj, property)) continue;
        value = obj[property];
        value = dumpObjectIndented(value, indent + "  ", true);
        result += indent + "'" + property + "' : " + value + ",\n";
      }
      out = "{\n";
      out += result;
      out += indent.slice(2);
      out += "}";
      if (!isProp) {
        out = indent + out;
      }
    }
    if (isArray) {
      if (obj.length === 0) {
        out = "[]";
      } else if (obj.length === 1) {
        out = "[" + dumpObjectIndented(obj[0], indent + "  ", true) + "]";
      } else {
        ods = (function() {
          var _i, _len, _results;
          _results = [];
          for (_i = 0, _len = obj.length; _i < _len; _i++) {
            item = obj[_i];
            _results.push(dumpObjectIndented(item, indent + "  ") + "\n");
          }
          return _results;
        })();
        out = "[ \n" + ods + "\n" + "]\n";
      }
    }
    out = out.replace(/\n,/g, ",\n");
    out = out.replace(/\n\n/g, "\n");
    return out;
  };
  ResourceFieldModel = (function() {
    __extends(ResourceFieldModel, Backbone.Model);
    function ResourceFieldModel() {
      ResourceFieldModel.__super__.constructor.apply(this, arguments);
    }
    return ResourceFieldModel;
  })();
  ResourceFieldView = (function() {
    __extends(ResourceFieldView, Backbone.View);
    function ResourceFieldView() {
      ResourceFieldView.__super__.constructor.apply(this, arguments);
    }
    ResourceFieldView.prototype.initialize = function(options) {
      return this.template = _.template($("#resource_field_template").html());
    };
    ResourceFieldView.prototype.render = function() {
      var data, flag, jqRendered, selector, _i, _len, _ref;
      data = this.model.toJSON();
      jqRendered = $(this.template(data));
      _ref = ['nullable', 'readonly', 'unique', 'blank'];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        flag = _ref[_i];
        selector = "span.flag_" + flag;
        jqRendered.find(selector).toggleClass('active_flag', data[flag]);
      }
      $(this.el).html(jqRendered);
      return this;
    };
    return ResourceFieldView;
  })();
  ResourceModel = (function() {
    __extends(ResourceModel, Backbone.Model);
    function ResourceModel() {
      ResourceModel.__super__.constructor.apply(this, arguments);
    }
    ResourceModel.prototype.initialize = function(options) {
      _.bindAll(this, 'modelChange');
      this.resourceName = options.resourceName;
      this.bind('change', this.modelChange);
      return ResourceModel.__super__.initialize.call(this, options);
    };
    ResourceModel.prototype.modelChange = function() {
      var args, fieldData, fieldName, _ref, _results;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      if (this.hasChanged("schema")) {
        this.url = this.get('schema');
        this.fetch();
        this.url = this.get("list_endpoint") + "example/";
        this.fetch({
          error: __bind(function() {
            this.set({
              POST: false
            });
            return this.set({
              GET: false
            });
          }, this)
        });
      }
      this.fields = [];
      _ref = this.toJSON().fields;
      _results = [];
      for (fieldName in _ref) {
        fieldData = _ref[fieldName];
        fieldData.default_value = fieldData["default"];
        fieldData.name = fieldName;
        _results.push(this.fields.push(new ResourceFieldModel(fieldData)));
      }
      return _results;
    };
    ResourceModel.prototype.loaded = function() {
      return this.toJSON()['fields'] !== void 0;
    };
    return ResourceModel;
  })();
  ResourceView = (function() {
    __extends(ResourceView, Backbone.View);
    function ResourceView() {
      ResourceView.__super__.constructor.apply(this, arguments);
    }
    ResourceView.prototype.el = "#resource";
    ResourceView.prototype.initialize = function(options) {
      _.bindAll(this, 'render');
      this.model || (this.model = new ResourceModel());
      this.model.bind('change', this.render);
      return this.template = _.template($("#resource_template").html());
    };
    ResourceView.prototype.formatExampleData = function(method, data) {
      var METHOD, allowed_methods, method_has_data, method_is_allowed;
      METHOD = method.toUpperCase();
      method = method.toLowerCase();
      allowed_methods = data.allowed_detail_http_methods.concat(data.allowed_list_http_methods);
      method_is_allowed = __indexOf.call(allowed_methods, method) >= 0;
      method_has_data = data[METHOD];
      if (method_is_allowed && method_has_data) {
        return data[METHOD] = dumpObjectIndented(data[METHOD]);
      } else {
        return data[METHOD] = "// not allowed";
      }
    };
    ResourceView.prototype.render = function() {
      var data, field, fieldView, jqFieldsList, _i, _len, _ref;
      $(this.el).empty();
      if (!this.model || !this.model.loaded()) {
        return this;
      }
      data = this.model.toJSON();
      data.resource_name = this.model.resourceName;
      this.formatExampleData('POST', data);
      this.formatExampleData('GET', data);
      $(this.el).html(this.template(data));
      jqFieldsList = $(this.el).find('.fields_list');
      _ref = this.model.fields;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        field = _ref[_i];
        fieldView = new ResourceFieldView({
          model: field
        });
        fieldView.render();
        jqFieldsList.append($(fieldView.el).html());
      }
      SyntaxHighlighter.highlight();
      return this;
    };
    return ResourceView;
  })();
  ResourceList = (function() {
    __extends(ResourceList, Backbone.Model);
    function ResourceList() {
      ResourceList.__super__.constructor.apply(this, arguments);
    }
    ResourceList.prototype.url = function() {
      return window.api_url;
    };
    return ResourceList;
  })();
  ResourceListView = (function() {
    __extends(ResourceListView, Backbone.View);
    function ResourceListView() {
      ResourceListView.__super__.constructor.apply(this, arguments);
    }
    ResourceListView.prototype.el = "#resource_list";
    ResourceListView.prototype.initialize = function() {
      _.bindAll(this, 'render');
      this.model.bind('change', this.render);
      this.resTemplate = _.template($("#resources_btn_template").html());
      this.currentModel = false;
      return this.currentModelView = new ResourceView();
    };
    ResourceListView.prototype.render = function() {
      var jqBtn, resourceName, resourceProps, tmpl_data, _fn, _ref;
      $(this.el).empty();
      _ref = this.model.toJSON();
      _fn = __bind(function(resourceName, resourceProps) {
        return jqBtn.click(__bind(function() {
          this.currentModelView.model.set(resourceProps);
          return this.currentModelView.model.resourceName = resourceName;
        }, this));
      }, this);
      for (resourceName in _ref) {
        resourceProps = _ref[resourceName];
        tmpl_data = {
          resource_name: resourceName
        };
        jqBtn = $(this.resTemplate(tmpl_data));
        _fn(resourceName, resourceProps);
        $(this.el).append(jqBtn);
      }
      return this.currentModelView.render();
    };
    return ResourceListView;
  })();
  $(document).ready(function() {
    var resources, resourcesView;
    resources = new ResourceList();
    resourcesView = new ResourceListView({
      model: resources
    });
    resources.fetch();
    return window.resourcesView = resourcesView;
  });
}).call(this);
