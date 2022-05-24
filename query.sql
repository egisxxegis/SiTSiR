SELECT inproc, 
author, 
booktitle, 
title, 
proc, 
ee, 
page, 
url, 
yr, 
abstract 
FROM (SELECT DISTINCT q_wejysunfoh.yr, 
q_wejysunfoh.booktitle, 
q_wejysunfoh.title, 
q_wejysunfoh.url, 
q_wejysunfoh.ee, 
q_wejysunfoh.page, 
q_wejysunfoh.proc, 
q_wejysunfoh.author, 
q_lguwjrxxqb.abstract, 
COALESCE(q_wejysunfoh.inproc, q_lguwjrxxqb.inproc) as "inproc" 
FROM (SELECT inproceedings_mgtxwbdgui.uri as "inproc", 
inproceedings_mgtxwbdgui.issued as "yr", 
inproceedings_mgtxwbdgui.booktitle as "booktitle", 
inproceedings_mgtxwbdgui.title as "title", 
inproceedings_mgtxwbdgui.homepage as "url", 
inproceedings_mgtxwbdgui.seealso as "ee", 
inproceedings_mgtxwbdgui.pages as "page", 
proceedings_cfbtnmdnvl.uri as "proc", 
person_fwlamxkeyf.uri as "author" 
FROM inproceedings AS inproceedings_mgtxwbdgui
INNER JOIN inproceedings_partof_proceedings AS inproceedings_partof_proceedings_uwkagqpdhk 
ON 1 
AND inproceedings_mgtxwbdgui.inproceedings_id = inproceedings_partof_proceedings_uwkagqpdhk.inproceedings_id1
INNER JOIN proceedings AS proceedings_cfbtnmdnvl 
ON 1 
AND inproceedings_partof_proceedings_uwkagqpdhk.proceedings_id2 = proceedings_cfbtnmdnvl.proceedings_id
INNER JOIN inproceedings_creator_person AS inproceedings_creator_person_hdnxmxpufh 
ON 1 
AND inproceedings_mgtxwbdgui.inproceedings_id = inproceedings_creator_person_hdnxmxpufh.inproceedings_id1
INNER JOIN person AS person_fwlamxkeyf 
ON 1 
AND inproceedings_creator_person_hdnxmxpufh.person_id2 = person_fwlamxkeyf.person_id
WHERE inproceedings_mgtxwbdgui.issued IS NOT NULL 
AND inproceedings_mgtxwbdgui.booktitle IS NOT NULL 
AND inproceedings_mgtxwbdgui.title IS NOT NULL 
AND inproceedings_mgtxwbdgui.homepage IS NOT NULL 
AND inproceedings_mgtxwbdgui.seealso IS NOT NULL 
AND inproceedings_mgtxwbdgui.pages IS NOT NULL) AS q_wejysunfoh
LEFT OUTER JOIN (SELECT inproceedings_hfuphapkdu.uri as "inproc", 
inproceedings_hfuphapkdu.abstract as "abstract" 
FROM inproceedings AS inproceedings_hfuphapkdu
WHERE inproceedings_hfuphapkdu.abstract IS NOT NULL) AS q_lguwjrxxqb 
ON 1 
AND 1 
AND ( q_wejysunfoh.inproc = q_lguwjrxxqb.inproc 
OR q_wejysunfoh.inproc IS NULL 
OR q_lguwjrxxqb.inproc IS NULL )
WHERE 1) AS result_q_rsytskenrm
WHERE 1 
ORDER BY yr