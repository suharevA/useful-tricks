SELECT product_name AS "Продукт",
       ids_history.is_name AS "ИС",
       sum(CPU) AS "CPU, шт.",
       round(avg(CPU_Util_Avg)) AS "CPU ср.утил., %",
       sum(round(CPU_recomended)) AS "CPU рекоменд., шт.",
       sum(round(Memory_GB)) AS "RAM, Гб",
       round(avg(Memory_Util_Avg)) AS "RAM ср.утил., %",
       sum(round(Memory_Recommended)) AS "RAM рекоменд., Гб",
       round(sum(round(Disk_Space))+mw.SizeMW-mwvm.SizeMW) AS "HDD предост. бл., Гб",
       sum(round(Guest_File_System_Curr_Util))AS "HDD использ. бл., Гб",
       SH.SizeSH AS "HDD предост. фл., Гб",
       SH.UsedSH AS "HDD использ. фл., Гб",
       ((sum(CPU_recomended)/sum(CPU))+(sum(Memory_Recommended)/sum(Memory_GB))) AS kf,
       mw.SizeMW,
       mwvm.SizeMW
FROM report
GLOBAL JOIN ids_history ON report.COD_ID = ids_history.server_id
LEFT JOIN (
    SELECT IS, sum(Size) AS SizeSH, sum(Used) AS UsedSH
    FROM share
    WHERE Add_time='2024-06-07' AND IS<>'is29-4 СРК' AND Volume NOT LIKE '%test%'
    GROUP BY IS
) SH ON ids_history.is_name = SH.IS
LEFT JOIN (
    SELECT IS, sum(Size) AS SizeMW
    FROM (SELECT IS, Filename, Size FROM MultiwriteDisk WHERE Add_time = '2024-06-07' GROUP BY IS, Filename, Size)
    GROUP BY IS
) mw ON ids_history.is_name = mw.IS
LEFT JOIN (
    SELECT IS, sum(Size) AS SizeMW
    FROM MultiwriteDisk
    WHERE Add_time = '2024-06-07'
    GROUP BY IS
) mwvm ON ids_history.is_name = mwvm.IS
WHERE toDate(report.Add_time) = '2024-06-07' AND
      ids_history.Add_time = '2024-06-07' AND
      report.Datacenter <> 'DC' AND
      product_name='ЦОД' AND
      report.Datacenter <>'mgmt-DC'
GROUP BY ids_history.product_name, ids_history.is_name, SH.SizeSH, SH.UsedSH, mw.SizeMW, mwvm.SizeMW
ORDER BY ids_history.is_name
LIMIT 10;