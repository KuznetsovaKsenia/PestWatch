const form=document.getElementById("assessment-form"),submit=document.getElementById("assessment-submit"),errorBox=document.getElementById("assessment-error"),section=document.getElementById("assessment-result"),meta=document.getElementById("assessment-result-meta"),container=document.getElementById("risk-results");
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
function payload(){const d=new FormData(form);return{location:{name:d.get("location_name"),region:d.get("location_region"),country:d.get("location_country")},profile:d.get("profile")}}
function publicError(b){if(b?.error?.code==="LOCATION_NOT_FOUND")return"Не удалось найти указанное местоположение. Проверьте населённый пункт и регион.";if(b?.error?.code==="LOCATION_SERVICE_UNAVAILABLE")return"Сервис определения местоположения временно недоступен. Попробуйте позже.";if(b?.error?.code==="INVALID_REQUEST")return"Проверьте заполненные данные и попробуйте снова.";return"Не удалось выполнить оценку. Попробуйте ещё раз."}
form.addEventListener("submit",async e=>{e.preventDefault();errorBox.hidden=true;submit.disabled=true;submit.textContent="Выполняется оценка...";try{const r=await fetch("/api/assessments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload())}),b=await r.json();if(!r.ok||!b.success){errorBox.textContent=publicError(b);errorBox.hidden=false;return}render(b.data)}catch(_){errorBox.textContent="Не удалось связаться с PestWatch. Попробуйте ещё раз.";errorBox.hidden=false}finally{submit.disabled=false;submit.textContent="Выполнить оценку"}});

// =====================================================================
// SLICE 3.2A — MODAL SHELL
// =====================================================================

const riskDetailsDialog=document.getElementById("risk-details-dialog");
const riskDetailsTitle=document.getElementById("risk-details-title");
const riskDetailsLevel=document.getElementById("risk-details-level");
const riskDetailsCalculation=document.getElementById("risk-details-calculation");

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
   detailRow("Дефицит насыщения воздуха влагой",saturation?.actual_value==null?"Нет данных":`${oneDecimal(saturation.actual_value)} мм рт. ст.`,detailState(saturation)),
   detailRow("Условие для оценки","менее 5 мм рт. ст."),
  ],"Дефицит насыщения показывает, насколько воздух сухой: чем меньше значение, тем более влажные условия."),
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
   detailRow(
    "Влияние на оценку риска",
    "Не влияет на текущую оценку риска"),
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

container.addEventListener("click",event=>{
 const trigger=event.target.closest(".risk-details-trigger");
 if(!trigger)return;

 const result=findRiskResult(trigger.dataset.threatCode);
 if(!result)return;

 bindRiskDetailsIdentity(result);
 bindCalculationDetails(result);
 openRiskDetailsModal(trigger)
});
