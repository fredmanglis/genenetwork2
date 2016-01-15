// Generated by CoffeeScript 1.8.0
(function() {
  var block_outliers, composite_mapping_fields, do_ajax_post, get_progress, mapping_method_fields, open_mapping_results, outlier_text, showalert, submit_special, toggle_enable_disable, update_time_remaining;

  submit_special = function(url) {
    //var url;
    console.log("In submit_special");
    console.log("this is:", this);
    console.log("$(this) is:", $(this));
    //url = $(this).data("url");
    console.log("url is:", url);
    $("#trait_data_form").attr("action", url);
    return $("#trait_data_form").submit();
  };

  update_time_remaining = function(percent_complete) {
    var minutes_remaining, now, period, total_seconds_remaining;
    now = new Date();
    period = now.getTime() - root.start_time;
    console.log("period is:", period);
    if (period > 8000) {
      total_seconds_remaining = (period / percent_complete * (100 - percent_complete)) / 1000;
      minutes_remaining = Math.round(total_seconds_remaining / 60);
      if (minutes_remaining < 3) {
        return $('#time_remaining').text(Math.round(total_seconds_remaining) + " seconds remaining");
      } else {
        return $('#time_remaining').text(minutes_remaining + " minutes remaining");
      }
    }
  };

  get_progress = function() {
    var params, params_str, temp_uuid, url;
    console.log("temp_uuid:", $("#temp_uuid").val());
    temp_uuid = $("#temp_uuid").val();
    params = {
      key: temp_uuid
    };
    params_str = $.param(params);
    url = "/get_temp_data?" + params_str;
    console.log("url:", url);
    $.ajax({
      type: "GET",
      url: url,
      success: (function(_this) {
        return function(progress_data) {
          var percent_complete;
          percent_complete = progress_data['percent_complete'];
          console.log("in get_progress data:", progress_data);
          $('#marker_regression_progress').css("width", percent_complete + "%");
          if (root.start_time) {
            if (!isNaN(percent_complete)) {
              return update_time_remaining(percent_complete);
            }
          } else {
            return root.start_time = new Date().getTime();
          }
        };
      })(this)
    });
    return false;
  };

  block_outliers = function() {
    return $('.outlier').each((function(_this) {
      return function(_index, element) {
        return $(element).find('.trait_value_input').val('x');
      };
    })(this));
  };

  do_ajax_post = function(url, form_data) {
    $.ajax({
      type: "POST",
      url: url,
      data: form_data,
      error: (function(_this) {
        return function(xhr, ajaxOptions, thrownError) {
          alert("Sorry, an error occurred");
          console.log(xhr);
          clearInterval(_this.my_timer);
          $('#progress_bar_container').modal('hide');
          $('#static_progress_bar_container').modal('hide');
          return $("body").html("We got an error.");
        };
      })(this),
      success: (function(_this) {
        return function(data) {
          clearInterval(_this.my_timer);
          $('#progress_bar_container').modal('hide');
          $('#static_progress_bar_container').modal('hide');
          return open_mapping_results(data);
        };
      })(this)
    });
    console.log("settingInterval");
    this.my_timer = setInterval(get_progress, 1000);
    return false;
  };

  open_mapping_results = function(data) {
    return $.colorbox({
      html: data,
      href: "#mapping_results_holder",
      height: "90%",
      width: "90%",
      onComplete: (function(_this) {
        return function() {
          var filename, getSvgXml;
          root.create_lod_chart();
          filename = "lod_chart_" + js_data.this_trait;
          getSvgXml = function() {
            var svg;
            svg = $("#topchart").find("svg")[0];
            return (new XMLSerializer).serializeToString(svg);
          };
          $("#exportform > #export").click(function() {
            var form, svg_xml;
            svg_xml = getSvgXml();
            form = $("#exportform");
            form.find("#data").val(svg_xml);
            form.find("#filename").val(filename);
            return form.submit();
          });
          return $("#exportpdfform > #export_pdf").click(function() {
            var form, svg_xml;
            svg_xml = getSvgXml();
            form = $("#exportpdfform");
            form.find("#data").val(svg_xml);
            form.find("#filename").val(filename);
            return form.submit();
          });
        };
      })(this)
    });
  };

  outlier_text = "One or more outliers exist in this data set. Please review values before mapping. Including outliers when mapping may lead to misleading results. We recommend <A HREF=\"http://en.wikipedia.org/wiki/Winsorising\">winsorising</A> the outliers or simply deleting them.";

  showalert = function(message, alerttype) {
    return $('#alert_placeholder').append('<div id="alertdiv" class="alert ' + alerttype + '"><a class="close" data-dismiss="alert">�</a><span>' + message + '</span></div>');
  };

  $('#suggestive').hide();

  $('input[name=display_all]').change((function(_this) {
    return function() {
      console.log("check");
      if ($('input[name=display_all]:checked').val() === "False") {
        return $('#suggestive').show();
      } else {
        return $('#suggestive').hide();
      }
    };
  })(this));

  $("#pylmm_mapping_compute").on("mouseover", (function(_this) {
    return function() {
      if ($(".outlier").length && $(".outlier-alert").length < 1) {
        return showalert(outlier_text, "alert-success outlier-alert");
      }
    };
  })(this));

  $("#pylmm_compute").on("click", (function(_this) {
    return function() {
      var form_data, url;
      //$("#progress_bar_container").modal();
      url = "/marker_regression";
      $('input[name=method]').val("pylmm");
      $('input[name=num_perm]').val($('input[name=num_perm_pylmm]').val());
      $('input[name=manhattan_plot]').val($('input[name=manhattan_plot_pylmm]:checked').val());
      form_data = $('#trait_data_form').serialize();
      console.log("form_data is:", form_data);
      return submit_special(url);
      //return do_ajax_post(url, form_data);
    };
  })(this));

  $("#rqtl_geno_compute").on("click", (function(_this) {
    return function() {
      var form_data, url;
      //$("#progress_bar_container").modal();
      url = "/marker_regression";
      $('input[name=method]').val("rqtl_geno");
      $('input[name=num_perm]').val($('input[name=num_perm_rqtl_geno]').val());
      $('input[name=manhattan_plot]').val($('input[name=manhattan_plot_rqtl]:checked').val());
      $('input[name=control_marker]').val($('input[name=control_rqtl_geno]').val());
      $('input[name=do_control]').val($('input[name=do_control_rqtl]:checked').val());
      form_data = $('#trait_data_form').serialize();
      console.log("form_data is:", form_data);
      return submit_special(url);
      //return do_ajax_post(url, form_data);
    };
  })(this));

  $("#plink_compute").on("click", (function(_this) {
    return function() {
      var form_data, url;
      //$("#static_progress_bar_container").modal();
      url = "/marker_regression";
      $('input[name=method]').val("plink");
      $('input[name=maf]').val($('input[name=maf_plink]').val());
      form_data = $('#trait_data_form').serialize();
      console.log("form_data is:", form_data);
      return submit_special(url);
      //return do_ajax_post(url, form_data);
    };
  })(this));

  $("#gemma_compute").on("click", (function(_this) {
    return function() {
      var form_data, url;
      console.log("RUNNING GEMMA");
      //$("#static_progress_bar_container").modal();
      url = "/marker_regression";
      $('input[name=method]').val("gemma");
      $('input[name=maf]').val($('input[name=maf_gemma]').val());
      form_data = $('#trait_data_form').serialize();
      console.log("form_data is:", form_data);
      return submit_special(url);
      //return do_ajax_post(url, form_data);
    };
  })(this));

  $("#interval_mapping_compute").on("click", (function(_this) {
    return function() {
      var form_data, url;
      console.log("In interval mapping");
      //$("#progress_bar_container").modal();
      url = "/marker_regression";
      $('input[name=method]').val("reaper");
      $('input[name=manhattan_plot]').val($('input[name=manhattan_plot_reaper]:checked').val());
      $('input[name=control_marker]').val($('input[name=control_reaper]').val());
      $('input[name=do_control]').val($('input[name=do_control_reaper]:checked').val());
      $('input[name=mapping_display_all]').val($('input[name=display_all_reaper]'));
      $('input[name=suggestive]').val($('input[name=suggestive_reaper]'));
      form_data = $('#trait_data_form').serialize();
      console.log("form_data is:", form_data);
      return submit_special(url);
      //return do_ajax_post(url, form_data);
    };
  })(this));

  $("#interval_mapping_compute").on("mouseover", (function(_this) {
    return function() {
      if ($(".outlier").length && $(".outlier-alert").length < 1) {
        return showalert(outlier_text, "alert-success outlier-alert");
      }
    };
  })(this));

  composite_mapping_fields = function() {
    return $(".composite_fields").toggle();
  };

  mapping_method_fields = function() {
    return $(".mapping_method_fields").toggle();
  };

  $("#use_composite_choice").change(composite_mapping_fields);

  $("#mapping_method_choice").change(mapping_method_fields);

  toggle_enable_disable = function(elem) {
    return $(elem).prop("disabled", !$(elem).prop("disabled"));
  };

  $("#choose_closet_control").change(function() {
    return toggle_enable_disable("#control_locus");
  });

  $("#display_all_lrs").change(function() {
    return toggle_enable_disable("#suggestive_lrs");
  });

}).call(this);
