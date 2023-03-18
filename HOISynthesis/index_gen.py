# -*- coding: utf-8 -*-
import os,sys,random

filelist = 'input_list.txt'
default_playbackspeed = 2
fid = open(filelist, 'r')
tot_files = [f.strip() for f in fid.readlines()]
fid.close()

for grp in range(5):
    category = ['bucket', 'kettle', 'laptop', 'pliers', 'scissors'][grp]
    files = []
    for file in tot_files:
        if file.split('/')[1] == category:
            files.append(file)
    random.shuffle(files)
    print(len(files))
    
    txt_block0 = '''score = 'nan';
      button = document.getElementsByName('score%d');
      for(var i = 0; i < button.length; i++){
          if(button[i].checked){
              score = button[i].id;
          }
      }
      text += '%s'+': '+score+'\\n';'''

    txt_block1 = '''<tr>
    <td width="60%%" valign="top">
      <video id="test%d" height="480" width="640" style="border-style: solid" align="top" controls>
        <source src="./%s" type="video/mp4">
      </video>
    </td>
    <td width="40%%" valign="top">
    <fieldset>
    <legend>请打分:</legend>
    <p>
      1分: <input type="radio" id=1 name="score%d" /><br />
      2分: <input type="radio" id=2 name="score%d" /><br />
      3分: <input type="radio" id=3 name="score%d" /><br />
      4分: <input type="radio" id=4 name="score%d" /><br />
      5分: <input type="radio" id=5 name="score%d" />
    </p>
    </fieldset>
    </td>
    </tr>'''

    txt_block2 = '''vid = document.getElementById("test%d");
    vid.defaultPlaybackRate = %d;
    vid.load();'''

    txt = '''<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>HOISynthesis</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    '''

    txt += '''<script language="Javascript" >
    function download(filename) {
      var button;
      var text='';
      var score;'''

    for i, line in enumerate(files):
      txt += txt_block0%(i, line)

    txt += '''var pom = document.createElement('a');
      pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
      pom.setAttribute('download', filename);
      pom.style.display = 'none';
      document.body.appendChild(pom);
      pom.click();
      document.body.removeChild(pom);
    }
    </script>
    </head>

    <body>
    <div>
    请按照视频的类人真实度、物理真实度对每段视频打分。<br>
    1分 - 视频动作和人类行为差别非常大，存在大量穿模、手部运动与物体运动不配套等物理不真实现象<br>
    2分 - 介于1分和3分之间<br>
    3分 - 视频具有一定的类人真实度和物理真实度，但仍能察觉到与人类行为的差异，或具有较为明显的物理缺陷<br>
    4分 - 介于3分和5分之间<br>
    5分 - 该视频与人类操作行为基本一致且物理真实<br><br>
    打分完毕后，在最下方文本框输入您的ID（姓名或昵称），下载文件并发还给请您打分的人<br><br><br>
    </div>

    <table width="100%" style="border-style: solid"><tbody>'''

    for i, line in enumerate(files):
      txt += txt_block1 % (i, line, i, i, i, i, i)

    txt += ('''</tbody></table>
    <br><br>
    <form onsubmit="download(this['name'].value+'_%d.txt')">
      <input type="text" name="name" value="请输入您的ID">
      <input type="submit" value="结果下载">
    </form>
    <script>
    var vid;''')%(grp)

    for i, line in enumerate(files):
      txt += txt_block2%(i, default_playbackspeed)

    txt += '''</script>
    </body></html>'''

    fid2 = open('group_{}.html'.format(grp), 'w', encoding="utf-8")
    fid2.write(txt)
    fid2.close()