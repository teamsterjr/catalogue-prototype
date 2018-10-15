var renderPipeline;
var config = { libraries: {}, stages: [] };
var deferreds = [];

templatePipeline = Handlebars.compile($("#pipelinetemplate").html());
templateMethod = Handlebars.compile($("#methodtemplate").html());
templateConfig = Handlebars.compile($("#configtemplate").html());

$(document).ready(function() {
  $.get("static/data/config.json", function(data) {
    config.methods = {};
    var stageMethods = {};
    config.pipeline = {libraries:{},...data.default_state};
    data.libraries.forEach(function(library) {
      manifestUrl = [library.repo, library.manifest].join("");
      deferreds.push(
        $.get(manifestUrl, function(manifestData) {
          libraryMethods = manifestData.methods;
          delete manifestData.methods;
          config.libraries[manifestData.key] = { ...library, ...manifestData };
          $.each(libraryMethods, function(name, method) {
            method.stage = method.stage || "Misc";
            method.key = manifestData.key + "." + name;

            config.methods[method.key] = {
              ...method,
              src: manifestData.key,
              isCore: manifestData.isCore,
              name: name
            };

            if (!stageMethods[method.stage]) {
              stageMethods[method.stage] = [];
            }
            stageMethods[method.stage].push(method.key);
          });
        })
      ); //push
    }); // libraries

    var defer = $.when.apply($, deferreds);
    defer.done(function() {
      data.stages.forEach(function(stage) {
        stage.methods = stageMethods[stage.name];
        config.stages.push(stage);
        if (stage.notTarget) {
          return;
        }
        pipelineStage = { ...stage, methods: [] };
        config.pipeline.stages = config.pipeline.stages || [];
        defaultMethods = stage.defaultMethods || [];
        delete stage.defaultMethods;
        defaultMethods.forEach(function(method) {
          method.key = [method.src, method.method].join(".");
          config.methods[method.key]["used"] = true;
          config.methods[method.key]["fixed"] = method.fixed;
          pipelineStage.methods.push(method.key);
        });
        config.pipeline.stages.push(pipelineStage);
      });
      render();
    });
  }); // fetch config
}); // doc.ready

Handlebars.registerHelper("isRemoveable", function(context, options) {
  return context.removeable && !this.fixed
    ? options.fn(this)
    : options.inverse(this);
});

function render() {
  renderMethods("methods", config);
  renderMethods("pipeline-list", {
    ...config.pipeline,
    methods: config.methods,
    removeable: true
  });
  renderPipeline();
  renderConfig();
  setSortable();
}

function renderConfig() {
  rendered = templateConfig(config.pipeline);
  $("#config" ).html(rendered);
  createString =
    '<a download="Jenkinsfile.yaml" href="data:application/octect-stream,' +
    encodeURI($("#config").text()) +
    '">Download</a>';
  $(createString).appendTo("#config");

}

function renderMethods(target, contents) {
  rendered = templateMethod(contents);
  $("#" + target).html(rendered);
}

function renderPipeline() {
  rendered = templatePipeline({ ...config.pipeline, methods: config.methods });
  $("#pipeline").html(rendered);
  createString =
    '<a download="Jenkinsfile" href="data:application/octect-stream,' +
    encodeURI($("#pipeline").text()) +
    '">Download</a>';
  $(createString).appendTo("#pipeline");
}

function updateList() {
  used = {methods:{},libraries:{}}
  $("#pipeline-list ul").each(function() {
    stage = $(this);
    stageMethods = [];
    stage.find("li").each(function() {
      method = $(this);
      key = method.data("key");
      src = method.data("src");
      if (key) {
        if (config.methods[key].stage != "Misc") {
          used.methods[key] = used.methods[key] || {}
          used.methods[key].used = (used.methods[key].used || 0) + 1;
          config.methods[key].used = used.methods[key].used
        }
        stageMethods.push(key);
      }
      if(src && !config.libraries[src].isCore) {
          used.libraries[src] = used.libraries[src] || {}
          used.libraries[src].used = (used.libraries[src].used || 0) + 1;
      }
    });
    config.pipeline.stages[stage.data("stage")].methods = stageMethods;
    config.pipeline.libraries = used.libraries
  });
  render();
}

function setSortable() {
  $("#pipeline-list ul").sortable({
    revert: true,
    items: "li:not(.fixed)",
    update: updateList
  });
  $("#methods ul li:not(.used):not(.fixed)").each(function() {
    $(this).draggable({
      helper: function(even, ui) {
        helper = $(this)
          .clone()
          .css("z-index", "5");
        return helper;
      },
      start: function() {
        target = $("#pipeline-list ul." + $(this).data("target"));
        target.addClass("active-target");
      },
      stop: function() {
        $('ul.active-target').removeClass('active-target')
      },
      revert: "invalid"
    });

    $(this).draggable(
      "option",
      "connectToSortable",
      "#pipeline-list ul." + $(this).data("target")
    );
  });
  $(".close").on("click", function() {
    method =
      config.methods[
        $(this)
          .parent()
          .data("key")
      ];
    method.used = (method.used || 1) - 1;
    $(this)
      .parent()
      .remove();
    updateList();
  });
  $("ul, li").disableSelection();
}
