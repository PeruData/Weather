*-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
* Create daily weather dataset 
* Author: SSB
* Last updated: December 16, 2018
*Clean extracted data from SENHAMI's webpage
*Prerequisite: "1.2 Clean Scrapped.py"
*Source: SENHAMI
* Reference period: 1990-2016
*-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
clear
timer clear
timer on 1
global ccc "/Volumes/Backup Mac/GRADE/Climate and Education/00_Data/"
cd "$ccc"

*1. Append between years
timer clear
timer on 1
	clear
	forvalues yy = 1990/2016 {  
		append using "in/SENHAMI/dta yearly/appended_`yy'.dta"
		}
	save "/Volumes/Backup Mac/GRADE/Climate and Education/00_Data/out/climate_90_16.dta", replace
timer off 1
timer list

*2. Process for analysis
use "/Volumes/Backup Mac/GRADE/Climate and Education/00_Data/out/climate_90_16.dta", clear

local clim_vars Precipitacion_mm_07 Precipitacion_mm_19 Temperatura_BulboSeco_c_07

foreach var in `clim_vars' { 
    destring `var', replace
	}

gen precipitation_cumm = Precipitacion_mm_07 + Precipitacion_mm_19 
rename Temperatura_BulboSeco_c_07 temperature_7am 

keep precipitation_cumm temperature_7am date station
rename station id_est
merge m:1 id_est using "/Volumes/Backup Mac/GRADE/Climate and Education/00_Data/in/SENHAMI/ubigeo_estaciones.dta", keep(1 3) nogen

destring temperature_7am, replace 
replace  temperature_7am    = . if !(temperature_7am    >= -30 & temp <= 40)
replace  precipitation_cumm = . if !(precipitation_cumm >= 0)

gen day_str   = substr(date,1,2)
gen month_str = substr(date,4,3)
gen year_str  = substr(date,8,4)

local months_ordered Ene Feb Mar Abr May Jun Jul Ago Sep Oct Nov Dic
local c = 1
foreach month_code in `months_ordered' {
    if `c'<10 {
	    local month_int = "0" + "`c'"
		}
	else local month_int = "`c'"	
	replace month_str = "`month_int'" if month_str == "`month_code'"
	local ++c
	}
gen t_str = day_str + "/" + month_str + "/" + year_str
gen t = date(t_str, "DMY")
replace t = 1990 + (t-10958)/365
sum temperature_7am, d

*3. Graph
local w1    w(0.1)
local w2    w(10)
local lcol1 color(maroon)
local lcol2 color(navy)
local msz   msize(vtiny)
local sav1 saving("Trash/g1.gph", replace)
local sav2 saving("Trash/g2.gph", replace)
local sav3 saving("Trash/g3.gph", replace)
local sav4 saving("Trash/g4.gph", replace)
local wht  graphregion(fcolor(white))
local xsc xscale(range(1990 2017))
local xlb xlabel(1990 (3) 2017, labsize(vsmall))

hist temperature_7am,    `w1' `lcol1' `sav1' `wht'  ti("Distribution of Temperature") subti("(°C, 7am)")  note("Note: u. of obs.: station-day")
hist precipitation_cumm, `w2' `lcol2' `sav2' `wht' ti("Distribution of Daily Precipitation") subti("(mm)") note("Note: u. of obs.: station-day")
save "/Volumes/Backup Mac/GRADE/Climate and Education/00_Data/out/climate_90_16.dta", replace 

collapse temperature_7am precipitation_cumm, by(t)
line  temperature_7am t, `msz' `wht' `lcol1' `sav3' ti("Average Temperature") subti("(°C, 7am)") lw(0.1) `xlb' `xsc'
line  precipitation_cumm t , `msz' `wht' `lcol2' `sav4'  ti("Average Precipitation") subti("(mm)") lw(0.1) `xlb' `xsc'

graph combine "Trash/g1.gph" "Trash/g2.gph"  "Trash/g3.gph"  "Trash/g4.gph", rows(2) `wht'



