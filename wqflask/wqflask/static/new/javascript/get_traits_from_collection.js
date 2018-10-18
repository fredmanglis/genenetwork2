// Generated by CoffeeScript 1.8.0
var add_trait_data, assemble_into_json, back_to_collections, collection_click, collection_list, color_by_trait, create_trait_data_csv, get_this_trait_vals, get_trait_data, process_traits, selected_traits, submit_click, this_trait_data, trait_click,
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

console.log("before get_traits_from_collection");

//collection_list = null;

this_trait_data = null;

selected_traits = {};

collection_click = function() {
  var this_collection_url;
  console.log("Clicking on:", $(this));
  this_collection_url = $(this).find('.collection_name').prop("href");
  this_collection_url += "&json";
  collection_list = $("#collections_holder").html();
  return $.ajax({
    dataType: "json",
    url: this_collection_url,
    success: process_traits
  });
};

submit_click = function() {
  var all_vals, sample, samples, scatter_matrix, this_trait_vals, trait, trait_names, trait_vals_csv, traits, _i, _j, _len, _len1, _ref;
  selected_traits = {};
  traits = [];
  $('#collections_holder').find('input[type=checkbox]:checked').each(function() {
    var this_dataset, this_trait, this_trait_url;
    this_trait = $(this).parents('tr').find('.trait').text();
    console.log("this_trait is:", this_trait);
    this_dataset = $(this).parents('tr').find('.dataset').text();
    console.log("this_dataset is:", this_dataset);
    this_trait_url = "/trait/get_sample_data?trait=" + this_trait + "&dataset=" + this_dataset;
    return $.ajax({
      dataType: "json",
      url: this_trait_url,
      async: false,
      success: add_trait_data
    });
  });
  trait_names = [];
  samples = $('input[name=allsamples]').val().split(" ");
  all_vals = [];
  this_trait_vals = get_this_trait_vals(samples);
  all_vals.push(this_trait_vals);
  _ref = Object.keys(selected_traits);
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    trait = _ref[_i];
    trait_names.push(trait);
    this_trait_vals = [];
    for (_j = 0, _len1 = samples.length; _j < _len1; _j++) {
      sample = samples[_j];
      if (__indexOf.call(Object.keys(selected_traits[trait]), sample) >= 0) {
        this_trait_vals.push(parseFloat(selected_traits[trait][sample]));
      } else {
        this_trait_vals.push(null);
      }
    }
    all_vals.push(this_trait_vals);
  }
  trait_vals_csv = create_trait_data_csv(selected_traits);
  scatter_matrix = new ScatterMatrix(trait_vals_csv);
  scatter_matrix.render();
  return $.colorbox.close();
};

create_trait_data_csv = function(selected_traits) {
  var all_vals, index, sample, sample_vals, samples, this_trait_vals, trait, trait_names, trait_vals_csv, _i, _j, _k, _l, _len, _len1, _len2, _len3, _ref;
  trait_names = [];
  trait_names.push($('input[name=trait_id]').val());
  samples = $('input[name=allsamples]').val().split(" ");
  all_vals = [];
  this_trait_vals = get_this_trait_vals(samples);
  all_vals.push(this_trait_vals);
  _ref = Object.keys(selected_traits);
  for (_i = 0, _len = _ref.length; _i < _len; _i++) {
    trait = _ref[_i];
    trait_names.push(trait);
    this_trait_vals = [];
    for (_j = 0, _len1 = samples.length; _j < _len1; _j++) {
      sample = samples[_j];
      if (__indexOf.call(Object.keys(selected_traits[trait]), sample) >= 0) {
        this_trait_vals.push(parseFloat(selected_traits[trait][sample]));
      } else {
        this_trait_vals.push(null);
      }
    }
    all_vals.push(this_trait_vals);
  }
  console.log("all_vals:", all_vals);
  trait_vals_csv = trait_names.join(",");
  trait_vals_csv += "\n";
  for (index = _k = 0, _len2 = samples.length; _k < _len2; index = ++_k) {
    sample = samples[index];
    if (all_vals[0][index] === null) {
      continue;
    }
    sample_vals = [];
    for (_l = 0, _len3 = all_vals.length; _l < _len3; _l++) {
      trait = all_vals[_l];
      sample_vals.push(trait[index]);
    }
    trait_vals_csv += sample_vals.join(",");
    trait_vals_csv += "\n";
  }
  return trait_vals_csv;
};

trait_click = function() {
  var dataset, this_trait_url, trait;
  console.log("Clicking on:", $(this));
  trait = $(this).parent().find('.trait').text();
  dataset = $(this).parent().find('.dataset').text();
  this_trait_url = "/trait/get_sample_data?trait=" + trait + "&dataset=" + dataset;
  $.ajax({
    dataType: "json",
    url: this_trait_url,
    success: get_trait_data
  });
  return $.colorbox.close();
};

add_trait_data = function(trait_data, textStatus, jqXHR) {
  var trait_name, trait_sample_data;
  trait_name = trait_data[0];
  trait_sample_data = trait_data[1];
  selected_traits[trait_name] = trait_sample_data;
  return console.log("selected_traits:", selected_traits);
};

populate_cofactor_info = function(trait_info) {
  if ($('input[name=selecting_which_cofactor]').val() == "1"){
    $('#cofactor1_trait_link').attr("href", trait_info['url'])
    if (trait_info['type'] == "ProbeSet"){
      $('#cofactor1_trait_link').text(trait_info['species'] + " " + trait_info['group'] + " " + trait_info['tissue'] + " " + trait_info['db'] + ": " + trait_info['name'])
      $('#cofactor1_description').text("[" + trait_info['symbol'] + " on " + trait_info['location'] + " Mb]\n" + trait_info['description'])
    } else {
      $('#cofactor1_trait_link').text(trait_info['species'] + " " + trait_info['group'] + " " + trait_info['db'] + ": " + trait_info['name'])
      $('#cofactor1_description').html('<a href=\"' + trait_info['pubmed_link'] + '\">PubMed: ' + trait_info['pubmed_text'] + '</a><br>' + trait_info['description'])
    }
    $('#select_cofactor1').text("Change Cofactor 1");
    $('#cofactor1_info_container').css("display", "inline");
    $('#cofactor2_button').css("display", "inline");
  } else {
    $('#cofactor2_trait_link').attr("href", trait_info['url'])
    if (trait_info['type'] == "ProbeSet"){
      $('#cofactor2_trait_link').text(trait_info['species'] + " " + trait_info['group'] + " " + trait_info['tissue'] + " " + trait_info['db'] + ": " + trait_info['name'])
      $('#cofactor2_description').text("[" + trait_info['symbol'] + " on " + trait_info['location'] + " Mb]\n" + trait_info['description'])
    } else {
      $('#cofactor2_trait_link').text(trait_info['species'] + " " + trait_info['group'] + " " + trait_info['db'] + ": " + trait_info['name'])
      $('#cofactor2_description').html('<a href=\"' + trait_info['pubmed_link'] + '\">PubMed: ' + trait_info['pubmed_text'] + '</a><br>' + trait_info['description'])
    }
    $('#select_cofactor2').text("Change Cofactor 2");
    $('#cofactor2_info_container').css("display", "inline");
  }
}

get_trait_data = function(trait_data, textStatus, jqXHR) {
  var sample, samples, this_trait_vals, trait_sample_data, vals, _i, _len;
  trait_sample_data = trait_data[1];
  if ( $('input[name=allsamples]').length ) {
    samples = $('input[name=allsamples]').val().split(" ");
  } else {
    samples = js_data.indIDs
  }
  sample_vals = [];
  vals = [];
  for (_i = 0, _len = samples.length; _i < _len; _i++) {
    sample = samples[_i];
    if (sample in trait_sample_data) {
      sample_vals.push(sample + ":" + parseFloat(trait_sample_data[sample]))
      vals.push(parseFloat(trait_sample_data[sample]))
    } else {
      sample_vals.push(null)
      vals.push(null)
    }
  }
  if ( $('input[name=allsamples]').length ) {
    if ($('input[name=samples]').length < 1) {
      $('#hidden_inputs').append('<input type="hidden" name="samples" value="[' + samples.toString() + ']" />');
    }
    $('#hidden_inputs').append('<input type="hidden" name="vals" value="[' + vals.toString() + ']" />');
    this_trait_vals = get_this_trait_vals(samples);
    return color_by_trait(trait_sample_data);
  } else{
    populate_cofactor_info(trait_data[0])
    sorted = vals.slice().sort(function(a,b){return a-b})
    ranks = vals.slice().map(function(v){ return sorted.indexOf(v)+1 });
    sample_ranks = []
    for (_i = 0; _i < samples.length; _i++){
      if (samples[_i] in trait_sample_data){
        sample_ranks.push(samples[_i] + ":" + ranks[_i])
      } else {
        sample_ranks.push(null)
      }
    }

    if ($('input[name=selecting_which_cofactor]').val() == "1"){
      $('input[name=cofactor1_vals]').val(sample_vals)
      $('input[name=ranked_cofactor1_vals]').val(sample_ranks)
    } else {
      $('input[name=cofactor2_vals]').val(sample_vals)
      $('input[name=ranked_cofactor2_vals]').val(sample_ranks)
    }
    chartupdatedata();
    chartupdate();
    return false
  }
};

get_this_trait_vals = function(samples) {
  var sample, this_trait_vals, this_val, this_vals_json, _i, _len;
  this_trait_vals = [];
  for (_i = 0, _len = samples.length; _i < _len; _i++) {
    sample = samples[_i];
    this_val = parseFloat($("input[name='value:" + sample + "']").val());
    if (!isNaN(this_val)) {
      this_trait_vals.push(this_val);
    } else {
      this_trait_vals.push(null);
    }
  }
  console.log("this_trait_vals:", this_trait_vals);
  this_vals_json = '[' + this_trait_vals.toString() + ']';
  return this_trait_vals;
};

assemble_into_json = function(this_trait_vals) {
  var json_data, json_ids, num_traits, samples;
  num_traits = $('input[name=vals]').length;
  samples = $('input[name=samples]').val();
  json_ids = samples;
  json_data = '[' + this_trait_vals;
  $('input[name=vals]').each((function(_this) {
    return function(index, element) {
      return json_data += ',' + $(element).val();
    };
  })(this));
  json_data += ']';
  return [json_ids, json_data];
};

color_by_trait = function(trait_sample_data, textStatus, jqXHR) {
  console.log('in color_by_trait:', trait_sample_data);
  return root.bar_chart.color_by_trait(trait_sample_data);
};

process_traits = function(trait_data, textStatus, jqXHR) {
  var the_html, trait, _i, _len;
  console.log('in process_traits with trait_data:', trait_data);
  the_html = "<button id='back_to_collections' class='btn btn-inverse btn-small'>";
  the_html += "<i class='icon-white icon-arrow-left'></i> Back </button>";
  the_html += "    <button id='submit' class='btn btn-primary btn-small'> Submit </button>";
  the_html += "<table class='table table-hover'>";
  the_html += "<thead><tr><th></th><th>Record</th><th>Data Set</th><th>Description</th><th>Mean</th></tr></thead>";
  the_html += "<tbody>";
  for (_i = 0, _len = trait_data.length; _i < _len; _i++) {
    trait = trait_data[_i];
    the_html += "<tr class='trait_line'>";
    the_html += "<td class='select_trait'><input type='checkbox' name='selectCheck' class='checkbox edit_sample_checkbox'></td>";
    the_html += "<td class='trait'>" + trait.name + "</td>";
    the_html += "<td class='dataset'>" + trait.dataset + "</td>";
    the_html += "<td>" + trait.description + "</td>";
    the_html += "<td>" + (trait.mean || '&nbsp;') + "</td></tr>";
  }
  the_html += "</tbody>";
  the_html += "</table>";
  the_html += "<div id=\"collection_list_html\" style=\"display: none;\">"
  the_html += collection_list
  the_html += "</div>"
  the_html += "<script type='text/javascript' src='/static/new/javascript/get_traits_from_collection.js'></script>"
  $("#collections_holder").html(the_html);
  return $('#collections_holder').colorbox.resize();
};

back_to_collections = function() {
  collection_list_html = $('#collection_list_html').html()
  $("#collections_holder").html(collection_list_html);
  $(document).on("click", ".collection_line", collection_click);
  return $('#collections_holder').colorbox.resize();
};

console.log("inside get_traits_from_collection");
$(".collection_line").on("click", collection_click);
$("#submit").on("click", submit_click);
$(".trait").on("click", trait_click);
$("#back_to_collections").on("click", back_to_collections);