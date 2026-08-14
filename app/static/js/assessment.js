const form=document.getElementById("assessment-form"),submit=document.getElementById("assessment-submit"),errorBox=document.getElementById("assessment-error"),section=document.getElementById("assessment-result"),meta=document.getElementById("assessment-result-meta"),container=document.getElementById("risk-results");
const locationNameInput=document.getElementById("location-name");
const locationRegionInput=document.getElementById("location-region");
const locationCountryInput=document.getElementById("location-country");
const demoLocationSelect=document.getElementById("demo-location-select");
const demoModeBadge=document.getElementById("demo-mode-banner");
const realLocationField=document.getElementById("real-location-field");
const demoLocationField=document.getElementById("demo-location-field");
const demoModeExit=document.getElementById("demo-mode-exit");

// =====================================================================
// EPIC 13 / SLICE 13.7 — DEMO MODE UI CONTRACT
//
// Demo mode is entered through ?demo=1 and then
// preserved in sessionStorage during navigation.
// The public form remains visually almost identical:
// - city becomes a fixed select;
// - region and country are filled automatically;
// - the backend receives only scenario_id + profile.
// =====================================================================

const demoScenarios=[
 {scenarioId:"DEMO_A",name:"Архангельск",region:"Архангельская область",country:"Россия"},
 {scenarioId:"DEMO_B",name:"Казань",region:"Республика Татарстан",country:"Россия"},
 {scenarioId:"DEMO_C",name:"Омск",region:"Омская область",country:"Россия"},
 {scenarioId:"DEMO_D",name:"Пермь",region:"Пермский край",country:"Россия"},
 {scenarioId:"DEMO_E",name:"Тула",region:"Тульская область",country:"Россия"},
 {scenarioId:"DEMO_F",name:"Курск",region:"Курская область",country:"Россия"},
 {scenarioId:"DEMO_G",name:"Томск",region:"Томская область",country:"Россия"},
];

const DEMO_MODE_STORAGE_KEY="pestwatch.demoMode";

function activateDemoModeFromUrl(){
 const requested=new URLSearchParams(
  window.location.search
 ).get("demo")==="1";

 if(requested){
  window.sessionStorage.setItem(
   DEMO_MODE_STORAGE_KEY,
   "true"
  )
 }
}

function isDemoMode(){
 return window.sessionStorage.getItem(
  DEMO_MODE_STORAGE_KEY
 )==="true"
}

function disableDemoMode(){
 window.sessionStorage.removeItem(
  DEMO_MODE_STORAGE_KEY
 )
}

activateDemoModeFromUrl();

function findDemoScenario(scenarioId){
 return demoScenarios.find(scenario=>scenario.scenarioId===scenarioId)||null
}

function populateDemoLocationSelect(){
 if(!demoLocationSelect)return;

 demoLocationSelect.innerHTML=[
  '<option value="">Выберите населённый пункт</option>',
  ...demoScenarios.map(
   scenario=>`<option value="${esc(scenario.scenarioId)}">${esc(scenario.name)}</option>`
  ),
 ].join("")
}

function applyDemoLocation(scenarioId){
 const scenario=findDemoScenario(scenarioId);

 if(!scenario){
  if(locationNameInput)locationNameInput.value="";
  if(locationRegionInput)locationRegionInput.value="";
  if(locationCountryInput)locationCountryInput.value="Россия";
  return
 }

 if(locationNameInput)locationNameInput.value=scenario.name;
 if(locationRegionInput)locationRegionInput.value=scenario.region;
 if(locationCountryInput)locationCountryInput.value=scenario.country
}

function resetAssessmentResult(){
 currentAssessment=null;

 if(section)section.hidden=true;
 if(container)container.innerHTML="";
 if(meta)meta.textContent=""
}

function configureDemoModeUi(){
 const demo=isDemoMode();

 if(demoModeBadge){
  demoModeBadge.hidden=!demo;
 }

 if(realLocationField){
  realLocationField.hidden=demo;
 }

 if(demoLocationField){
  demoLocationField.hidden=!demo;
 }

 if(locationNameInput){
  locationNameInput.required=!demo;
 }

 if(demoLocationSelect){
  demoLocationSelect.required=demo;
 }

 if(locationRegionInput){
  locationRegionInput.readOnly=demo;

  if(!demo){
   locationRegionInput.value="";
  }
 }

 if(locationCountryInput){
  locationCountryInput.readOnly=demo;

  if(demo){
   locationCountryInput.value="Россия";
  }
 }
}

if(demoModeExit){
 demoModeExit.addEventListener("click",event=>{
  event.preventDefault();
  disableDemoMode();
  window.location.href="/";
 })
}

const profiles={HUMAN:"Человек",VEGETABLE_GARDEN:"Огород",GARDEN:"Сад"};
const threats={TICK:"Клещи",COLORADO_BEETLE:"Колорадский жук",CABBAGE_APHID:"Капустная тля",CODLING_MOTH:"Яблонная плодожорка"};
const levels={LOW:"НИЗКИЙ РИСК",MODERATE:"УМЕРЕННЫЙ РИСК",ELEVATED:"ПОВЫШЕННЫЙ РИСК",HIGH:"ВЫСОКИЙ РИСК"};
const states={MATCHED:"Условие выполнено",NOT_MATCHED:"Условие не выполнено",MISSING:"Недостаточно данных"};
function esc(v){const e=document.createElement("div");e.textContent=String(v);return e.innerHTML}
function dateRu(v){if(!v)return"—";const p=v.split("-");return p.length===3?`${p[2]}-${p[1]}-${p[0]}`:v}
function round(v){if(v===null||v===undefined)return null;const n=Number(v);return Number.isFinite(n)?Math.round(n):null}
function oneDecimal(v){if(v===null||v===undefined)return null;const n=Number(v);return Number.isFinite(n)?n.toFixed(1).replace(".",","):null}
function temperatureValue(v){if(v===null||v===undefined)return null;const n=Number(v);if(!Number.isFinite(n))return null;return Number.isInteger(n)?String(n):n.toFixed(1).replace(".",",")}
function observationTime(v){if(!v)return null;const match=String(v).match(/T(\d{2}):(\d{2})/);return match?`${match[1]}:${match[2]}`:null}
function weather(a){return a?.input_snapshot?.current_weather||null}
function weatherSummary(a){const w=weather(a);if(!w)return"";const temperature=temperatureValue(w.temperature),humidity=round(w.humidity),precipitation=oneDecimal(w.precipitation),wind=oneDecimal(w.wind_speed),time=observationTime(w.observed_at);
 const item=(icon,label,value)=>`<div class="weather-item"><span class="weather-item__icon" aria-hidden="true">${icon}</span><div><strong>${esc(value)}</strong><span>${esc(label)}</span></div></div>`;
 return `<section class="weather-summary" aria-label="Погода сейчас"><div class="weather-summary__title"><strong>ПОГОДА СЕЙЧАС</strong>${time?`<span>Данные на ${esc(time)}</span>`:""}</div><div class="weather-summary__items">${item("🌡","Температура",temperature===null?"—":`${temperature} °C`)}${item("💧","Влажность",humidity===null?"—":`${humidity} %`)}${item("🌧","Осадки",precipitation===null?"—":`${precipitation} мм`)}${item("💨","Ветер",wind===null?"—":`${wind} м/с`)}</div></section>`}
function factorView(f,threatCode,a){const v=temperatureValue(f.actual_value);
 if(f.factor==="AIR_TEMPERATURE"&&threatCode==="TICK")return{title:"Температура воздуха",now:v===null?"Сейчас: нет данных":`Сейчас: ${v} °C`,target:"Для активности клещей: от 10 °C",text:f.state==="MATCHED"?"Температурные условия позволяют клещам быть активными.":"Температура сейчас ниже порога потенциальной активности клещей."};
 if(f.factor==="AIR_TEMPERATURE"&&threatCode==="CABBAGE_APHID")return{title:"Температура воздуха",now:v===null?"Сейчас: нет данных":`Сейчас: ${v} °C`,target:"Благоприятный диапазон: 15–25 °C",text:f.state==="MATCHED"?"Температурные условия благоприятны для развития капустной тли.":"Температура сейчас вне благоприятного диапазона для развития капустной тли."};
 if(f.factor==="AIR_TEMPERATURE")return{title:"Температура воздуха",now:v===null?"Сейчас: нет данных":`Сейчас: ${v} °C`,target:null,text:f.explanation||""};
 if(f.factor==="SATURATION_DEFICIT"){const humidity=round(weather(a)?.humidity);return{title:"Влажность воздуха",now:humidity===null?"Сейчас: нет данных":`Сейчас: ${humidity} %`,target:"Для активности важен достаточно влажный воздух",text:f.state==="MATCHED"?"Воздух достаточно влажный для активности клещей.":"Воздух сейчас слишком сухой для длительной активности клещей."};}
 if(f.factor==="RELATIVE_HUMIDITY")return{title:"Относительная влажность",now:v===null?"Сейчас: нет данных":`Сейчас: ${v} %`,target:null,text:f.explanation||""};
 if(f.factor==="SOIL_TEMPERATURE_10CM")return{title:"Температура почвы",now:v===null?"Расчётная температура: нет данных":`Расчётная температура на глубине 10 см: около ${v} °C`,target:"Для начала активности: от 11 °C",text:f.state==="MATCHED"?"Почва достаточно прогрелась для активности вредителя.":"Почва ещё недостаточно прогрелась для активности вредителя."};
 if(f.factor==="DEGREE_DAYS_ABOVE_10C")return{title:"Сезонная активность",now:null,target:null,text:f.state==="MATCHED"?"Накопленного с начала сезона тепла достаточно для периода возможной сезонной активности вредителя.":"Накопленного с начала сезона тепла пока недостаточно для периода возможной сезонной активности вредителя."};
 return{title:"Фактор риска",now:v===null?null:`Текущее значение: ${v}`,target:null,text:f.explanation||""}}
function factorHtml(f,threatCode,a){const p=factorView(f,threatCode,a),s=(f.state||"MISSING").toLowerCase(),details=[p.now,p.target].filter(Boolean).map(x=>`<span>${esc(x)}</span>`).join("");
 return `<li class="factor-item factor-item--${esc(s)}"><div class="factor-head"><strong>${esc(p.title)}</strong><span class="factor-state">${esc(states[f.state]||"Нет данных")}</span></div>${details?`<div class="factor-details">${details}</div>`:""}<p>${esc(p.text)}</p></li>`}
function humidityInfo(r,a){if(r.threat_code!=="CABBAGE_APHID")return"";const h=round(weather(a)?.humidity);return `<li class="factor-item factor-item--info"><div class="factor-head"><strong>Относительная влажность</strong><span class="factor-state">Справочно</span></div><div class="factor-details"><span>${h===null?"Сейчас: нет данных":`Сейчас: ${esc(h)} %`}</span></div><p>Погодное наблюдение показывается справочно и в текущей модели не влияет на уровень риска капустной тли.</p></li>`}
function summary(r){if(r.status==="ERROR")return"Не удалось получить данные, необходимые для оценки этой угрозы.";if(r.status==="INSUFFICIENT_DATA")return"Для уверенной оценки пока недостаточно наблюдений.";if(r.threat_code==="TICK"){const matched=(r.factors||[]).filter(f=>f.state==="MATCHED").length;return matched===2?"Температура и влажность воздуха поддерживают потенциальную активность иксодовых клещей.":matched===1?"Только часть погодных условий сейчас поддерживает потенциальную активность иксодовых клещей.":"Текущие погодные условия ограничивают потенциальную активность иксодовых клещей.";}if(r.threat_code==="CABBAGE_APHID")return r.factors?.[0]?.state==="MATCHED"?"Температурные условия сейчас благоприятны для развития капустной тли.":"Температурные условия сейчас менее благоприятны для развития капустной тли.";if(r.threat_code==="CODLING_MOTH")return r.factors?.[0]?.state==="MATCHED"?"Температурные условия для сезонной активности яблонной плодожорки уже сформировались.":"Температурные условия для сезонной активности яблонной плодожорки ещё не сформировались.";return r.explanation}
function season(a){return a.profile==="GARDEN"&&a.historical_start_date?`<div class="season-period"><strong>Сезонный период</strong><span>Начало: ${esc(dateRu(a.historical_start_date))}</span><span>Наблюдения по: ${esc(dateRu(a.assessment_date))}</span></div>`:""}
function card(r,a){const level=(r.risk_level||"unknown").toLowerCase(),factors=(r.factors||[]).map(f=>factorHtml(f,r.threat_code,a)).join("")+humidityInfo(r,a);return `<article class="risk-card"><div class="risk-head"><h3>${esc(threats[r.threat_code]||r.threat_code)}</h3><div class="risk-level risk-level--${esc(level)}">${esc(levels[r.risk_level]||"РИСК НЕ ОПРЕДЕЛЁН")}</div></div><p class="risk-summary">${esc(summary(r))}</p>${season(a)}<ul class="factor-list">${factors}</ul><div class="risk-actions"><button class="risk-details-trigger" type="button" data-threat-code="${esc(r.threat_code)}">Рекомендации и источники →</button></div></article>`}

let currentAssessment=null;

function render(a){currentAssessment=a;meta.textContent=[profiles[a.profile]||a.profile,a.location.name,a.location.region,dateRu(a.assessment_date)].join(" · ");container.innerHTML=weatherSummary(a)+a.risk_results.map(r=>card(r,a)).join("");section.hidden=false;section.scrollIntoView({behavior:"smooth",block:"start"})}

function assessmentPayload(){
 const d=new FormData(form);

 if(isDemoMode()){
  return{
   scenario_id:demoLocationSelect?.value||"",
   profile:d.get("profile"),
  }
 }

 return{
  location:{
   name:d.get("location_name"),
   region:d.get("location_region"),
   country:d.get("location_country"),
  },
  profile:d.get("profile"),
 }
}

function assessmentEndpoint(){
 return isDemoMode()
  ?"/api/assessments/demo"
  :"/api/assessments"
}

function publicError(b){
 if(b?.error?.code==="LOCATION_NOT_FOUND")return"Не удалось найти указанное местоположение. Проверьте населённый пункт и регион.";
 if(b?.error?.code==="LOCATION_SERVICE_UNAVAILABLE")return"Сервис определения местоположения временно недоступен. Попробуйте позже.";
 if(b?.error?.code==="DEMO_SCENARIO_NOT_FOUND")return"Не удалось запустить выбранный демонстрационный сценарий. Выберите населённый пункт ещё раз.";
 if(b?.error?.code==="INVALID_REQUEST")return"Проверьте заполненные данные и попробуйте снова.";
 return"Не удалось выполнить оценку. Попробуйте ещё раз."
}

if(demoLocationSelect){
 demoLocationSelect.addEventListener("change",()=>{
  const scenario=findDemoScenario(
   demoLocationSelect.value
  );

  if(!scenario){
   if(locationRegionInput){
    locationRegionInput.value="";
   }

   if(locationCountryInput){
    locationCountryInput.value="Россия";
   }

   return;
  }

  if(locationRegionInput){
   locationRegionInput.value=scenario.region;
  }

  if(locationCountryInput){
   locationCountryInput.value=scenario.country;
  }
 });
}

configureDemoModeUi();

form.addEventListener("submit",async e=>{
 e.preventDefault();
 errorBox.hidden=true;

 if(isDemoMode()&&!demoLocationSelect?.value){
  errorBox.textContent="Выберите населённый пункт.";
  errorBox.hidden=false;
  return
 }

 submit.disabled=true;
 submit.textContent="Выполняется оценка...";

 try{
  const r=await fetch(assessmentEndpoint(),{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify(assessmentPayload())
  });
  const b=await r.json();

  if(!r.ok||!b.success){
   errorBox.textContent=publicError(b);
   errorBox.hidden=false;
   return
  }

  render(b.data)
 }catch(_){
  errorBox.textContent="Не удалось связаться с PestWatch. Попробуйте ещё раз.";
  errorBox.hidden=false
 }finally{
  submit.disabled=false;
  submit.textContent="Выполнить оценку"
 }
});

// =====================================================================
// SLICE 3.2A — MODAL SHELL
// =====================================================================

const riskDetailsDialog=document.getElementById("risk-details-dialog");
const riskDetailsTitle=document.getElementById("risk-details-title");
const riskDetailsLevel=document.getElementById("risk-details-level");
const riskDetailsCalculation=document.getElementById("risk-details-calculation");
const riskDetailsRecommendations=document.getElementById("risk-details-recommendations");
const riskDetailsSources=document.getElementById("risk-details-sources");
const riskDetailsMeaning=document.getElementById("risk-details-meaning");
const riskDetailsInputs=document.getElementById("risk-details-inputs");

let riskDetailsReturnFocus=null;

function openRiskDetailsModal(triggerElement=null){
 if(!riskDetailsDialog)return;
 riskDetailsReturnFocus=triggerElement instanceof HTMLElement?triggerElement:document.activeElement;
 if(!riskDetailsDialog.open)riskDetailsDialog.showModal();
 const closeButton=riskDetailsDialog.querySelector(".details-modal__close");
 if(closeButton)closeButton.focus()
}

function closeRiskDetailsModal(){
 if(riskDetailsDialog&&riskDetailsDialog.open)riskDetailsDialog.close()
}

if(riskDetailsDialog){
 riskDetailsDialog.addEventListener("click",event=>{
  if(event.target===riskDetailsDialog)closeRiskDetailsModal()
 });
 riskDetailsDialog.addEventListener("close",()=>{
  if(riskDetailsReturnFocus&&typeof riskDetailsReturnFocus.focus==="function")riskDetailsReturnFocus.focus();
  riskDetailsReturnFocus=null
 })
}

// =====================================================================
// SLICE 3.2B — THREAT BINDING
// The modal is bound to the RiskResult already present in currentAssessment.
// No API request and no recalculation happen here.
// =====================================================================

function findRiskResult(threatCode){
 if(!currentAssessment)return null;
 return (currentAssessment.risk_results||[]).find(
  result=>result.threat_code===threatCode
 )||null
}

function bindRiskDetailsIdentity(result){
 if(!result)return;

 const threatName=threats[result.threat_code]||result.threat_code;
 const levelCode=result.risk_level||"unknown";
 const levelClass=levelCode.toLowerCase();

 riskDetailsTitle.textContent=threatName;
 riskDetailsLevel.textContent=levels[result.risk_level]||"РИСК НЕ ОПРЕДЕЛЁН";
 riskDetailsLevel.className=`risk-level risk-level--${levelClass}`
}

// =====================================================================
// SLICE 3.3 — CALCULATION DETAILS
// Presentation only: values come from RiskResult + AssessmentInputSnapshot.
// No environmental values are recalculated in the browser.
// =====================================================================

function findFactor(result,factorCode){
 return (result?.factors||[]).find(
  factor=>factor.factor===factorCode
 )||null
}

function detailState(factor){
 if(!factor)return"Нет данных";
 return states[factor.state]||"Нет данных"
}

function detailRow(label,value,state=null){
 return `<div class="calculation-row"><span class="calculation-row__label">${esc(label)}</span><strong class="calculation-row__value">${esc(value)}</strong>${state?`<span class="calculation-row__state">${esc(state)}</span>`:""}</div>`
}

function detailBlock(title,rows,note=null){
 return `<div class="calculation-block"><h4>${esc(title)}</h4><div class="calculation-block__rows">${rows.join("")}</div>${note?`<p class="calculation-block__note">${esc(note)}</p>`:""}</div>`
}

function tickCalculationDetails(result,assessment){
 const temperature=findFactor(result,"AIR_TEMPERATURE");
 const saturation=findFactor(result,"SATURATION_DEFICIT");
 const w=weather(assessment);
 const matched=(result.factors||[]).filter(f=>f.state==="MATCHED").length;
 const known=(result.factors||[]).filter(f=>f.state!=="MISSING").length;

 return [
  detailBlock("Температура воздуха",[
   detailRow("Сейчас",temperature?.actual_value==null?"Нет данных":`${temperatureValue(temperature.actual_value)} °C`,detailState(temperature)),
   detailRow("Условие для оценки","от 10 °C"),
  ]),
  detailBlock("Влажность воздуха",[
   detailRow("Относительная влажность",w?.humidity==null?"Нет данных":`${oneDecimal(w.humidity)} %`),
   detailRow("Дефицит влажности воздуха",saturation?.actual_value==null?"Нет данных":`${oneDecimal(saturation.actual_value)} мм рт. ст.`,detailState(saturation)),
   detailRow("Условие для оценки","менее 5 мм рт. ст."),
  ],"Дефицит влажности показывает, насколько воздух сухой: чем меньше значение, тем более влажные условия."),
  detailBlock("Итог",[
   detailRow("Выполнено условий",`${matched} из ${known}`),
   detailRow("Уровень риска",levels[result.risk_level]||"Не определён"),
  ]),
 ].join("")
}

function cabbageAphidCalculationDetails(result,assessment){
 const temperature=findFactor(result,"AIR_TEMPERATURE");
 const w=weather(assessment);

 return [
  detailBlock("Температура воздуха",[
   detailRow("Сейчас",temperature?.actual_value==null?"Нет данных":`${temperatureValue(temperature.actual_value)} °C`,detailState(temperature)),
   detailRow("Благоприятный диапазон","15–25 °C"),
  ]),
  detailBlock("Относительная влажность",[
   detailRow("Сейчас",w?.humidity==null?"Нет данных":`${oneDecimal(w.humidity)} %`,"Справочно"),
   detailRow("Участие в уровне риска","Не влияет на текущую оценку риска"),
  ]),
  detailBlock("Итог",[
   detailRow("Уровень риска",levels[result.risk_level]||"Не определён"),
  ]),
 ].join("")
}

function coloradoBeetleCalculationDetails(result,assessment){
 const factor=findFactor(result,"SOIL_TEMPERATURE_10CM");
 const estimate=assessment?.input_snapshot?.soil_temperature_10cm_estimate;
 const sourceDepths=estimate?.source_depths_cm||[];
 const sourceTemperatures=estimate?.source_temperatures||[];

 const sourceRows=sourceDepths.map((depth,index)=>
  detailRow(
   `Температура почвы на глубине ${oneDecimal(depth)} см`,
   sourceTemperatures[index]==null?"Нет данных":`${temperatureValue(sourceTemperatures[index])} °C`
  )
 );

 return [
  detailBlock("Исходные данные о почве",sourceRows.length?sourceRows:[
   detailRow("Исходные температуры","Нет данных")
  ]),
  detailBlock("Расчёт PestWatch",[
   detailRow("Температура почвы на глубине 10 см",factor?.actual_value==null?"Нет данных":`${temperatureValue(factor.actual_value)} °C`,detailState(factor)),
   detailRow("Метод расчёта",estimate?.method==="LINEAR_INTERPOLATION"?"Линейная интерполяция":(estimate?.method||"Нет данных")),
  ],"Линейная интерполяция рассчитывает промежуточную температуру между известными значениями на глубине 6 и 18 см."),
  detailBlock("Условие для оценки",[
   detailRow("Для начала активности","от 11 °C"),
  ]),
  detailBlock("Итог",[
   detailRow("Уровень риска",levels[result.risk_level]||"Не определён"),
  ]),
 ].join("")
}

function codlingMothCalculationDetails(result,assessment){
 const factor=findFactor(result,"DEGREE_DAYS_ABOVE_10C");
 const degreeDays=assessment?.input_snapshot?.degree_days_10c;

 return [
  detailBlock("Температурный сезон",[
   detailRow("Начало сезона",dateRu(assessment?.historical_start_date)),
   detailRow("Как определено","3 дня подряд со средней температурой выше 10 °C"),
   detailRow("Наблюдения по",dateRu(assessment?.assessment_date)),
  ],"PestWatch считает началом сезона первый день первых трёх последовательных дней со средней суточной температурой выше 10 °C. С этой даты начинается накопление эффективных температур."),
  detailBlock("Расчёт PestWatch",[
   detailRow("Базовая температура",degreeDays?.base_temperature==null?"Нет данных":`${temperatureValue(degreeDays.base_temperature)} °C`),
   detailRow("Накопленная сумма эффективных температур",degreeDays?.total==null?"Нет данных":`${oneDecimal(degreeDays.total)} градусо-дня`,detailState(factor)),
  ]),
  detailBlock("Условие для оценки",[
   detailRow("Условие для температурной оценки сезонной активности","130 градусо-дней"),
  ]),
  detailBlock("Итог",[
   detailRow("Уровень риска",levels[result.risk_level]||"Не определён"),
  ]),
 ].join("")
}

function calculationDetailsHtml(result,assessment){
 if(!result||!assessment){
  return `<p class="details-modal__placeholder">Данные расчёта недоступны.</p>`
 }

 if(result.status==="ERROR"){
  return `<p class="details-modal__placeholder">Расчёт не был завершён из-за недоступности необходимых данных.</p>`
 }

 if(result.threat_code==="TICK")return tickCalculationDetails(result,assessment);
 if(result.threat_code==="CABBAGE_APHID")return cabbageAphidCalculationDetails(result,assessment);
 if(result.threat_code==="COLORADO_BEETLE")return coloradoBeetleCalculationDetails(result,assessment);
 if(result.threat_code==="CODLING_MOTH")return codlingMothCalculationDetails(result,assessment);

 return `<p class="details-modal__placeholder">Подробности расчёта для этой угрозы пока недоступны.</p>`
}

function bindCalculationDetails(result){
 if(!riskDetailsCalculation)return;
 riskDetailsCalculation.innerHTML=calculationDetailsHtml(
  result,
  currentAssessment
 )
}



// =====================================================================
// SLICE 3.4B — RECOMMENDATIONS UI
// Recommendations are presentation-only guidance derived from the
// persisted RiskResult. They do not fetch data, recalculate risk,
// confirm pest presence, or automatically recommend chemical treatment.
// =====================================================================

function recommendationItem(title,text,tone="default"){
 return `<div class="recommendation-item recommendation-item--${esc(tone)}"><h4>${esc(title)}</h4><p>${esc(text)}</p></div>`
}

function tickRecommendations(result){
 const higherRisk=["ELEVATED","HIGH"].includes(result.risk_level);

 if(higherRisk){
  return [
   recommendationItem(
    "Что делать сейчас",
    "Погодные условия позволяют клещам сохранять активность. При посещении леса, парков и мест с высокой травой используйте закрытую светлую одежду, средства защиты от клещей и регулярно осматривайте одежду и тело. После возвращения осмотрите также домашних животных.",
    "attention"
   ),
   recommendationItem(
    "На что обратить внимание",
    "Клещи могут находиться в высокой траве, кустарнике и лесной подстилке. Осматривайте одежду и открытые участки тела во время прогулки и после возвращения."
   ),
   recommendationItem(
    "Важно",
    "PestWatch оценивает погодные условия для возможной активности клещей, но не определяет их фактическое наличие в конкретном месте.",
    "note"
   ),
  ].join("")
 }

 return [
  recommendationItem(
   "Что делать сейчас",
   "Текущая погода менее благоприятна для активности клещей, но это не означает, что клещей рядом нет. При прогулках в лесу, парках и местах с высокой травой всё равно стоит соблюдать меры защиты."
  ),
  recommendationItem(
   "На что обратить внимание",
   "Если планируется прогулка по высокой траве, кустарнику или лесу, после возвращения осмотрите одежду, тело и домашних животных."
  ),
  recommendationItem(
   "Важно",
   "Низкая температурно-погодная оценка не означает отсутствия клещей.",
   "note"
  ),
 ].join("")
}

function cabbageAphidRecommendations(result){
 const higherRisk=["ELEVATED","HIGH"].includes(result.risk_level);

 return [
  recommendationItem(
   "Что делать сейчас",
   higherRisk
    ?"Температурные условия благоприятны для развития капустной тли. Осмотрите молодые листья, точки роста и формирующиеся кочаны или соцветия, особенно нижнюю сторону листьев."
    :"Сейчас температура менее благоприятна для быстрого развития тли. Это не означает её отсутствия — продолжайте периодически осматривать растения.",
   higherRisk?"attention":"default"
  ),
  recommendationItem(
   "На что обратить внимание",
   "Если вы обнаружили тлю, осмотрите несколько растений и оцените, насколько широко она распространилась. Обратите внимание, много ли тли на листьях и молодых побегах и есть ли заметные повреждения. Не спешите с обработкой при единичных насекомых: божьи коровки и некоторые другие полезные насекомые питаются тлёй и могут сдерживать её численность."
  ),
  recommendationItem(
   "Важно",
   "Удаляйте крестоцветные сорняки — например, пастушью сумку: на них тля может сохраняться и размножаться рядом с посадками.",
   "note"
  ),
 ].join("")
}

function coloradoBeetleRecommendations(result){
 const higherRisk=["ELEVATED","HIGH"].includes(result.risk_level);

 return [
  recommendationItem(
   "Что делать сейчас",
   higherRisk
    ?"Почва прогрелась до температуры, при которой перезимовавшие колорадские жуки могут начинать выходить на поверхность. Усильте осмотр посадок."
    :"Почва пока менее благоприятна для начала выхода перезимовавших колорадских жуков. Продолжайте периодически осматривать посадки.",
   higherRisk?"attention":"default"
  ),
  recommendationItem(
   "На что обратить внимание",
   "Осматривайте картофель и другие паслёновые культуры — например, томаты и баклажаны — на наличие взрослых жуков, кладок яиц и молодых личинок."
  ),
  recommendationItem(
   "Важно",
   "Удаляйте рядом с посадками картофеля паслёновые сорняки, например чёрный паслён. По возможности не выращивайте картофель несколько лет подряд на одном и том же месте — чередуйте его с другими культурами.",
   "note"
  ),
 ].join("")
}

function codlingMothRecommendations(result){
 const higherRisk=["ELEVATED","HIGH"].includes(result.risk_level);

 return [
  recommendationItem(
   "Что делать сейчас",
   higherRisk
    ?"Накопленного тепла достаточно для периода возможной сезонной активности яблонной плодожорки. Осматривайте яблони и плоды, а для более точного определения фазы активности используйте феромонные ловушки."
    :"Температурный показатель пока ниже рабочего порога PestWatch для периода возможной сезонной активности яблонной плодожорки. Продолжайте периодически осматривать деревья и плоды.",
   higherRisk?"attention":"default"
  ),
  recommendationItem(
   "На что обратить внимание",
   "Обращайте внимание на повреждения плодов и результаты феромонных ловушек. Они помогают понять, наблюдается ли фактическая активность вредителя."
  ),
  recommendationItem(
   "Важно",
   "Температурная оценка PestWatch не подтверждает фактический лёт плодожорки. Для более точного определения начала лёта используют феромонные ловушки.",
   "note"
  ),
 ].join("")
}

function recommendationsHtml(result){
 if(!result){
  return `<p class="details-modal__placeholder">Рекомендации недоступны.</p>`
 }

 if(result.status==="ERROR"){
  return `<p class="details-modal__placeholder">Рекомендации не сформированы, потому что оценка не была завершена из-за недоступности необходимых данных.</p>`
 }

 if(result.status==="INSUFFICIENT_DATA"){
  return `<p class="details-modal__placeholder">Для уверенных рекомендаций пока недостаточно данных. Продолжайте обычное наблюдение за возможной угрозой.</p>`
 }

 if(result.threat_code==="TICK")return tickRecommendations(result);
 if(result.threat_code==="CABBAGE_APHID")return cabbageAphidRecommendations(result);
 if(result.threat_code==="COLORADO_BEETLE")return coloradoBeetleRecommendations(result);
 if(result.threat_code==="CODLING_MOTH")return codlingMothRecommendations(result);

 return `<p class="details-modal__placeholder">Рекомендации для этой угрозы пока недоступны.</p>`
}

function bindRecommendations(result){
 if(!riskDetailsRecommendations)return;
 riskDetailsRecommendations.innerHTML=recommendationsHtml(result)
}




// =====================================================================
// SLICE 3.4C-B — SOURCES UI
// Static source registry for the user-facing evidence behind calculations,
// methodology and recommendations. No runtime network request is made.
// =====================================================================

const sourcePurposeLabels={
 CALCULATION:"Для расчёта",
 METHODOLOGY:"Методика расчёта",
 RECOMMENDATION:"Для рекомендаций",
};

const riskSourceRegistry={
 TICK:[
  {
   title:"Ixodes ricinus и влажность воздуха",
   organization:"Научная публикация",
   purpose:"CALCULATION",
   description:"Подтверждает влияние дефицита насыщения воздуха влагой на активность клещей и ориентир менее 5 мм рт. ст.",
   url:"https://pmc.ncbi.nlm.nih.gov/articles/PMC4311481/",
  },
  {
   title:"Профилактика инфекций, передающихся с укусами клещей",
   organization:"Роспотребнадзор",
   purpose:"RECOMMENDATION",
   description:"Подтверждает практические меры защиты: светлую закрытую одежду, регулярные осмотры и специальные средства защиты от клещей.",
   url:"https://urpngt.rospotrebnadzor.ru/osnovnie-napravlenija/sanitarnyjj-nadzor/5356-2020-05-08-13-49-05.html",
  },
 ],
 CABBAGE_APHID:[
  {
   title:"Влияние температуры на капустную тлю Brevicoryne brassicae",
   organization:"Научная публикация",
   purpose:"CALCULATION",
   description:"Подтверждает диапазон 15–25 °C как благоприятный для увеличения популяции капустной тли.",
   url:"https://pmc.ncbi.nlm.nih.gov/articles/PMC6303750/",
  },
  {
   title:"Cabbage Aphid — Cole Crops",
   organization:"University of California IPM",
   purpose:"RECOMMENDATION",
   description:"Подтверждает рекомендации по осмотру растений, сохранению естественных врагов тли и удалению крестоцветных растений рядом с посадками.",
   url:"https://ipm.ucanr.edu/agriculture/cole-crops/cabbage-aphid/",
  },
 ],
 COLORADO_BEETLE:[
  {
   title:"Pest categorisation of Leptinotarsa decemlineata",
   organization:"Европейское агентство по безопасности пищевых продуктов",
   purpose:"CALCULATION",
   description:"Подтверждает ориентир температуры почвы 11 °C для начала выхода перезимовавших взрослых колорадских жуков.",
   url:"https://efsa.onlinelibrary.wiley.com/doi/10.2903/j.efsa.2020.6359",
  },
  {
   title:"Colorado potato beetle",
   organization:"University of Minnesota Extension",
   purpose:"RECOMMENDATION",
   description:"Подтверждает рекомендации по осмотру посадок, работе с яйцами и личинками, паслёновыми сорняками и чередованию места выращивания картофеля.",
   url:"https://extension.umn.edu/yard-and-garden-insects/colorado-potato-beetle",
  },
 ],
 CODLING_MOTH:[
  {
   title:"Codling Moth — Phenology Models",
   organization:"University of California IPM",
   purpose:"METHODOLOGY",
   description:"Подтверждает применение температурных моделей и градусо-дней для оценки сезонного развития яблонной плодожорки. Не подтверждает конкретный порог PestWatch 130 градусо-дней.",
   url:"https://ipm.ucanr.edu/weather/phenology-models-description/codling-moth/",
  },
  {
   title:"Codling Moth — Apple",
   organization:"University of California IPM",
   purpose:"RECOMMENDATION",
   description:"Подтверждает использование феромонных ловушек для наблюдения за фактической активностью плодожорки и определения точки отсчёта температурной модели.",
   url:"https://ipm.ucanr.edu/agriculture/apple/codling-moth/",
  },
 ],
};

function sourceItem(source){
 const purpose=sourcePurposeLabels[source.purpose]||source.purpose;

 return `<article class="source-item"><div class="source-item__head"><div><span class="source-item__organization">${esc(source.organization)}</span><h4>${esc(source.title)}</h4></div><span class="source-purpose source-purpose--${esc(source.purpose.toLowerCase())}">${esc(purpose)}</span></div><p>${esc(source.description)}</p><a class="source-link" href="${esc(source.url)}" target="_blank" rel="noopener noreferrer">Открыть источник ↗</a></article>`
}

function sourcesHtml(result){
 if(!result){
  return `<p class="details-modal__placeholder">Источники недоступны.</p>`
 }

 const sources=riskSourceRegistry[result.threat_code]||[];

 if(!sources.length){
  return `<p class="details-modal__placeholder">Источники для этой угрозы пока недоступны.</p>`
 }

 return sources.map(sourceItem).join("")
}

function bindSources(result){
 if(!riskDetailsSources)return;
 riskDetailsSources.innerHTML=sourcesHtml(result)
}




// =====================================================================
// SLICE 3.5 — RESULT MEANING
// Explains what the persisted RiskLevel means for the selected threat.
// It does not infer pest presence and does not recalculate risk.
// =====================================================================

function resultMeaningBlock(text,note){
 return `<div class="result-meaning__summary"><p>${esc(text)}</p></div><div class="result-meaning__note"><strong>Важно</strong><p>${esc(note)}</p></div>`
}

function isHigherRisk(result){
 return ["ELEVATED","HIGH"].includes(result?.risk_level)
}

function tickResultMeaning(result){
 if(isHigherRisk(result)){
  return resultMeaningBlock(
   "Погодные условия сейчас благоприятны для потенциальной активности клещей. Температура и влажность позволяют им дольше оставаться активными.",
   "Высокая оценка риска означает благоприятные погодные условия, а не подтверждённое наличие клещей в конкретном месте."
  )
 }

 return resultMeaningBlock(
  "Текущая погода менее благоприятна для активности клещей. Это может снижать вероятность их активного поведения, но не означает, что клещей рядом нет.",
  "PestWatch оценивает погодные условия, а не фактическое количество клещей на территории."
 )
}

function cabbageAphidResultMeaning(result){
 if(isHigherRisk(result)){
  return resultMeaningBlock(
   "Температура сейчас находится в диапазоне, благоприятном для развития капустной тли. При наличии тли на растениях такие условия могут способствовать увеличению её численности.",
   "PestWatch не определяет, есть ли тля на конкретных растениях. Это можно установить только при осмотре посадок."
  )
 }

 return resultMeaningBlock(
  "Температура сейчас менее благоприятна для быстрого развития капустной тли. Это может замедлять увеличение её численности, но не означает отсутствия тли на растениях.",
  "PestWatch оценивает температурные условия для развития тли, а её фактическое наличие определяется осмотром посадок."
 )
}

function coloradoBeetleResultMeaning(result){
 if(isHigherRisk(result)){
  return resultMeaningBlock(
   "Температура почвы достигла уровня, при котором перезимовавшие колорадские жуки могут начинать выходить на поверхность.",
   "Оценка показывает подходящие температурные условия, но не подтверждает, что жуки уже появились на ваших посадках."
  )
 }

 return resultMeaningBlock(
  "Температура почвы пока ниже уровня, при котором обычно начинается выход перезимовавших колорадских жуков.",
  "Низкая оценка риска не означает полного отсутствия вредителя — фактическое наличие определяется осмотром растений."
 )
}

function codlingMothResultMeaning(result){
 if(isHigherRisk(result)){
  return resultMeaningBlock(
   "Накопленного с начала температурного сезона тепла достаточно для периода возможной сезонной активности яблонной плодожорки.",
   "Это температурный индикатор PestWatch. Он не подтверждает фактический лёт плодожорки."
  )
 }

 return resultMeaningBlock(
  "Накопленного тепла пока недостаточно для достижения рабочего температурного порога PestWatch, связанного с периодом возможной сезонной активности яблонной плодожорки.",
  "Температурная оценка сама по себе не определяет наличие вредителя или фактическое начало лёта."
 )
}

function resultMeaningHtml(result){
 if(!result){
  return `<p class="details-modal__placeholder">Объяснение результата недоступно.</p>`
 }

 if(result.status==="ERROR"){
  return `<p class="details-modal__placeholder">Результат не был рассчитан из-за недоступности необходимых данных.</p>`
 }

 if(result.status==="INSUFFICIENT_DATA"){
  return resultMeaningBlock(
   "Для этой угрозы пока недостаточно данных, чтобы определить уровень риска.",
   "Недостаток данных не означает отсутствия угрозы. PestWatch не делает вывод о риске без необходимых наблюдений."
  )
 }

 if(result.threat_code==="TICK")return tickResultMeaning(result);
 if(result.threat_code==="CABBAGE_APHID")return cabbageAphidResultMeaning(result);
 if(result.threat_code==="COLORADO_BEETLE")return coloradoBeetleResultMeaning(result);
 if(result.threat_code==="CODLING_MOTH")return codlingMothResultMeaning(result);

 return `<p class="details-modal__placeholder">Объяснение для этой угрозы пока недоступно.</p>`
}

function bindResultMeaning(result){
 if(!riskDetailsMeaning)return;
 riskDetailsMeaning.innerHTML=resultMeaningHtml(result)
}




// =====================================================================
// SLICE 3.6 — INPUT DATA SUMMARY
// Shows which persisted observations were used for the selected threat.
// Presentation only: no extra request and no recalculation.
// =====================================================================

function inputDataRow(label,value,note=null){
 return `<div class="input-data-row"><span class="input-data-row__label">${esc(label)}</span><strong class="input-data-row__value">${esc(value)}</strong>${note?`<span class="input-data-row__note">${esc(note)}</span>`:""}</div>`
}

function inputDataBlock(title,rows,note=null){
 return `<div class="input-data-block"><h4>${esc(title)}</h4><div class="input-data-block__rows">${rows.join("")}</div>${note?`<p class="input-data-block__note">${esc(note)}</p>`:""}</div>`
}

function observedAtLabel(value){
 if(!value)return"Нет данных";
 const datePart=String(value).slice(0,10);
 const time=observationTime(value);
 return time?`${dateRu(datePart)}, ${time}`:dateRu(datePart)
}

function tickInputDataSummary(assessment){
 const w=weather(assessment);
 return [inputDataBlock("Текущие погодные наблюдения",[
  inputDataRow("Температура воздуха",w?.temperature==null?"Нет данных":`${temperatureValue(w.temperature)} °C`),
  inputDataRow("Относительная влажность",w?.humidity==null?"Нет данных":`${oneDecimal(w.humidity)} %`),
  inputDataRow("Время наблюдения",observedAtLabel(w?.observed_at)),
 ],"Эти погодные данные используются для оценки температурных и влажностных условий активности клещей.")].join("")
}

function cabbageAphidInputDataSummary(assessment){
 const w=weather(assessment);
 return [inputDataBlock("Текущие погодные наблюдения",[
  inputDataRow("Температура воздуха",w?.temperature==null?"Нет данных":`${temperatureValue(w.temperature)} °C`,"Используется в оценке"),
  inputDataRow("Относительная влажность",w?.humidity==null?"Нет данных":`${oneDecimal(w.humidity)} %`,"Показывается справочно"),
  inputDataRow("Время наблюдения",observedAtLabel(w?.observed_at)),
 ],"В текущей оценке капустной тли уровень риска определяется температурой воздуха. Влажность отображается как дополнительная информация.")].join("")
}

function coloradoBeetleInputDataSummary(assessment){
 const estimate=assessment?.input_snapshot?.soil_temperature_10cm_estimate;
 const sourceDepths=estimate?.source_depths_cm||[];
 const sourceTemperatures=estimate?.source_temperatures||[];
 const w=weather(assessment);
 const rows=sourceDepths.map((depth,index)=>inputDataRow(`Температура почвы на глубине ${oneDecimal(depth)} см`,sourceTemperatures[index]==null?"Нет данных":`${temperatureValue(sourceTemperatures[index])} °C`));
 if(!rows.length)rows.push(inputDataRow("Исходные температуры почвы","Нет данных"));
 rows.push(inputDataRow("Время погодного наблюдения",observedAtLabel(w?.observed_at)));
 return [inputDataBlock("Исходные данные о почве",rows,"По этим наблюдениям PestWatch рассчитывает температуру почвы на глубине 10 см. Сам расчёт показан в разделе «Как рассчитано».")].join("")
}

function codlingMothInputDataSummary(assessment){
 const degreeDays=assessment?.input_snapshot?.degree_days_10c;
 const observations=degreeDays?.observations||[];
 const known=observations.filter(observation=>observation?.mean_temperature!==null&&observation?.mean_temperature!==undefined).length;
 return [inputDataBlock("Исторические температурные наблюдения",[
  inputDataRow("Период",degreeDays?.period_start&&degreeDays?.period_end?`${dateRu(degreeDays.period_start)} — ${dateRu(degreeDays.period_end)}`:"Нет данных"),
  inputDataRow("Наблюдений с температурой",observations.length?`${known} из ${observations.length}`:"Нет данных"),
  inputDataRow("Начало температурного сезона",assessment?.historical_start_date?dateRu(assessment.historical_start_date):"Не определено"),
 ],"Используются среднесуточные температуры текущего года. Из них определяется начало температурного сезона и накапливается сумма эффективных температур.")].join("")
}

function inputDataSummaryHtml(result,assessment){
 if(!result||!assessment)return `<p class="details-modal__placeholder">Исходные данные недоступны.</p>`;
 if(result.threat_code==="TICK")return tickInputDataSummary(assessment);
 if(result.threat_code==="CABBAGE_APHID")return cabbageAphidInputDataSummary(assessment);
 if(result.threat_code==="COLORADO_BEETLE")return coloradoBeetleInputDataSummary(assessment);
 if(result.threat_code==="CODLING_MOTH")return codlingMothInputDataSummary(assessment);
 return `<p class="details-modal__placeholder">Исходные данные для этой угрозы пока недоступны.</p>`
}

function bindInputDataSummary(result){
 if(!riskDetailsInputs)return;
 riskDetailsInputs.innerHTML=inputDataSummaryHtml(result,currentAssessment)
}


container.addEventListener("click",event=>{
 const trigger=event.target.closest(".risk-details-trigger");
 if(!trigger)return;

 const result=findRiskResult(trigger.dataset.threatCode);
 if(!result)return;

 bindRiskDetailsIdentity(result);
 bindResultMeaning(result);
 bindRecommendations(result);
 bindCalculationDetails(result);
 bindInputDataSummary(result);
 bindSources(result);
 openRiskDetailsModal(trigger)
});
