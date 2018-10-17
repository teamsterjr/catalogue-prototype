var data = {{include_json('../config/config.json','../config/libraries.json')}};
var templateMethod = "{{ include_raw('method.mst') }}";
var templateConfig = "{{ include_raw('config.mst','\\n') }}";
var templatePipeline = "{{include_raw('pipeline.mst','\\n') }}"