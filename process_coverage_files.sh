#!/usr/bin/env bash

cov_report_dir="docs"

replace_str1="_Volumes_Mac HD_data_Files_eclipse_workspace_workspace_work_minicondas_4_4_10_envs_eman-deps-11-gui_bin_"
replace_str2="/Volumes/Mac HD/data/Files/eclipse_workspace/workspace_work/minicondas/4.4.10/envs/eman-deps-11-gui/bin/"

IFS=','
for f in `ls -m "${cov_report_dir}/${replace_str1}"*`;do
    ff=$(echo "$f" | tr -d '\n')
    ff=${ff# }
    ff2=${ff/${replace_str1}/}
    mv -v "$ff" $ff2
done

sed -i.bak -e "s/${replace_str1}//g" ${cov_report_dir}/index.html ${cov_report_dir}/status.json ${cov_report_dir}/*.html
rm ${cov_report_dir}/*.bak

sed -i.bak -e "s?${replace_str2}??g" ${cov_report_dir}/index.html ${cov_report_dir}/status.json ${cov_report_dir}/*.html
rm ${cov_report_dir}/*.bak

replace_str1="_Volumes_Mac HD_data_Files_eclipse_workspace_workspace_work_minicondas_4_4_10_envs_eman-deps-11-gui_lib_python2_7_site-packages_"
replace_str2="/Volumes/Mac HD/data/Files/eclipse_workspace/workspace_work/minicondas/4.4.10/envs/eman-deps-11-gui/lib/python2.7/site-packages/"

IFS=','
for f in `ls -m "${cov_report_dir}/${replace_str1}"*`;do
    ff=$(echo "$f" | tr -d '\n')
    ff=${ff# }
    ff2=${ff/${replace_str1}/}
    mv -v "$ff" $ff2
done

sed -i.bak -e "s/${replace_str1}//g" ${cov_report_dir}/index.html ${cov_report_dir}/status.json ${cov_report_dir}/*.html
rm ${cov_report_dir}/*.bak

sed -i.bak -e "s?${replace_str2}??g" ${cov_report_dir}/index.html ${cov_report_dir}/status.json ${cov_report_dir}/*.html
rm ${cov_report_dir}/*.bak
