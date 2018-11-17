*-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
* Create daily weather dataset 
* Author: SSB
* Last updated: November 16, 2018
*Clean raw data from SENHAMI's webpage
*Prerequisite: "1.2 Clean Scrapped.py"
*Source: SENHAMI
* Reference period: 1990-2016
*-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  
clear
timer clear
timer on 1
global ccc "/Volumes/Backup Mac/GRADE/Climate and Education/00_Data/"
cd "$ccc"

*1. Append raw yearly weather datasets
	clear
	forvalues yy = 1990/2016 {  
		append using "in/SENHAMI/to_stata/appended_`yy'.dta"
		}
	save "out/climate_90_16.dta", replace
*15s

*2. Clean weather data
*[any modification to the original SENHAMI variables is contained in this block]
	use "out/climate_90_16.dta", clear
	local clim_vars Precipitacion_mm_07 Precipitacion_mm_19 Temperatura_BulboSeco_c_07
	foreach var in `clim_vars' { 
		destring `var', replace
		}
	
	gen precipitation_cumm = Precipitacion_mm_07 + Precipitacion_mm_19 
	rename Temperatura_BulboSeco_c_07 temperature_7am 
	
	keep precipitation_cumm temperature_7am date station
	
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
	save "out/climate_90_16.dta", replace
*27s
	
*3. Bring in Station Characteristics
	use "out/climate_90_16.dta", clear
	*every station with data should be matched
	merge m:1 station using "in/SENHAMI/to_stata/station characteristics.dta", nogen keep(1 3)
	drop if latitude == -999
	destring altitude, replace
	save "out/climate_90_16.dta", replace
*16s
