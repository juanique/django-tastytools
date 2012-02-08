(function() {
  var ResourceFieldModel, ResourceFieldView, ResourceList, ResourceListView, ResourceModel, ResourceView, dumpObjectIndented,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; },
    __slice = Array.prototype.slice,
    __indexOf = Array.prototype.indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  dumpObjectIndented = function(obj, indent, isProp) {
    var isArray, isBoolean, isNumber, isObject, isString, item, ods, out, property, result, value;
    if (indent == null) indent = "";
    if (isProp == null) isProp = false;
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
      if (!isProp) out = indent + out;
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

  ResourceFieldModel = (function(_super) {

    __extends(ResourceFieldModel, _super);

    function ResourceFieldModel() {
      ResourceFieldModel.__super__.constructor.apply(this, arguments);
    }

    return ResourceFieldModel;

  })(Backbone.Model);

  ResourceFieldView = (function(_super) {

    __extends(ResourceFieldView, _super);

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

  })(Backbone.View);

  ResourceModel = (function(_super) {

    __extends(ResourceModel, _super);

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
      var args, fieldData, fieldName, _ref, _results,
        _this = this;
      args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
      if (this.hasChanged("schema")) {
        this.url = this.get('schema');
        this.fetch();
        this.url = this.get("list_endpoint") + "example/";
        this.fetch({
          error: function() {
            _this.set({
              POST: false
            });
            return _this.set({
              GET: false
            });
          }
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

  })(Backbone.Model);

  ResourceView = (function(_super) {

    __extends(ResourceView, _super);

    function ResourceView() {
      ResourceView.__super__.constructor.apply(this, arguments);
    }

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

    ResourceView.prototype.highlightIfAllowed = function(data, action, method) {
      var allowed_methods, selector;
      selector = "." + action + "_methods ." + method + "_method";
      allowed_methods = data["allowed_" + action + "_http_methods"];
      return $(this.el).find(selector).toggleClass('allowed', __indexOf.call(allowed_methods, method) >= 0);
    };

    ResourceView.prototype.render = function() {
      var action, data, field, fieldView, jqFieldsList, method, _i, _j, _k, _len, _len2, _len3, _ref, _ref2, _ref3;
      $(this.el).empty();
      if (!this.model || !this.model.loaded()) return this;
      data = this.model.toJSON();
      data.resource_name = this.model.resourceName;
      this.formatExampleData('POST', data);
      this.formatExampleData('GET', data);
      $(this.el).html(this.template(data));
      jqFieldsList = $(this.el).find('ul.fields_list');
      _ref = ['list', 'detail'];
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        action = _ref[_i];
        _ref2 = ['get', 'post', 'delete', 'put', 'patch'];
        for (_j = 0, _len2 = _ref2.length; _j < _len2; _j++) {
          method = _ref2[_j];
          this.highlightIfAllowed(data, action, method);
        }
      }
      _ref3 = this.model.fields;
      for (_k = 0, _len3 = _ref3.length; _k < _len3; _k++) {
        field = _ref3[_k];
        fieldView = new ResourceFieldView({
          model: field
        });
        fieldView.render();
        jqFieldsList.append(fieldView.el);
      }
      SyntaxHighlighter.highlight();
      return this;
    };

    return ResourceView;

  })(Backbone.View);

  ResourceList = (function(_super) {

    __extends(ResourceList, _super);

    function ResourceList() {
      ResourceList.__super__.constructor.apply(this, arguments);
    }

    ResourceList.prototype.url = function() {
      return window.api_url;
    };

    return ResourceList;

  })(Backbone.Model);

  ResourceListView = (function(_super) {

    __extends(ResourceListView, _super);

    function ResourceListView() {
      ResourceListView.__super__.constructor.apply(this, arguments);
    }

    ResourceListView.prototype.initialize = function() {
      _.bindAll(this, 'render');
      this.model.bind('change', this.render);
      this.resTemplate = _.template($("#resources_btn_template").html());
      this.currentModel = false;
      return this.currentModelView = new ResourceView();
    };

    ResourceListView.prototype.render = function() {
      var jqBtn, resourceName, resourceProps, tmpl_data, _fn, _ref,
        _this = this;
      $(this.el).empty();
      _ref = this.model.toJSON();
      _fn = function(resourceProps) {
        return jqBtn.click(function() {
          return _this.currentModelView.model.set(resourceProps);
        });
      };
      for (resourceName in _ref) {
        resourceProps = _ref[resourceName];
        tmpl_data = {
          resource_name: resourceName
        };
        jqBtn = $(this.resTemplate(tmpl_data));
        _fn(resourceProps);
        $(this.el).append(jqBtn);
      }
      this.currentModelView.render();
      $(this.el).append(this.currentModelView.el);
      return $('#resource_list').empty().append(this.el);
    };

    return ResourceListView;

  })(Backbone.View);

  $(document).ready(function() {
    var resources, resourcesView;
    console.log("document ready");
    resources = new ResourceList();
    resourcesView = new ResourceListView({
      model: resources
    });
    resources.fetch();
    return window.resourcesView = resourcesView;
  });

}).call(this);
