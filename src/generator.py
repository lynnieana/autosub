########################################################################
# generator.py -- Generates the individual tasks when needed
#
# Copyright (C) 2015 Andreas Platschek <andi.platschek@gmail.com>
#                    Martin  Mosbeck   <martin.mosbeck@gmx.at>
# License GPL V2 or later (see http://www.gnu.org/licenses/gpl2.txt)
########################################################################

import threading
import sqlite3 as lite
import datetime
import logger, common
import os

class taskGenerator (threading.Thread):
   def __init__(self, threadID, name, gen_queue, sender_queue, logger_queue):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.gen_queue = gen_queue
      self.sender_queue = sender_queue
      self.logger_queue = logger_queue

   ####
   # log_a_msg()
   ####
   def log_a_msg(self, msg, loglevel):
      self.logger_queue.put(dict({"msg": msg, "type": loglevel, "loggername": self.name}))

   def run(self):
      self.log_a_msg("Task Generator thread started", "INFO")

      while True:
         next_gen_msg = self.gen_queue.get(True) #blocking wait on gen_queue
         TaskNr=next_gen_msg.get('TaskNr')
         UserId=next_gen_msg.get('UserId')
         UserEmail=next_gen_msg.get('UserEmail')
         MessageId=next_gen_msg.get('MessageId')

         # check if there is a generator executable configured in the database -- if not fall back on static
         # generator script.
         curc, conc = self.connect_to_db('course.db')
         sql_cmd="SELECT GeneratorExecutable FROM TaskConfiguration WHERE TaskNr == "+str(TaskNr)
         curc.execute(sql_cmd);
         generatorname = curc.fetchone();
    
         if str(generatorname[0]) != 'None':
            sql_cmd="SELECT PathToTask FROM TaskConfiguration WHERE TaskNr == "+str(TaskNr)
            curc.execute(sql_cmd);
            path = curc.fetchone();
            scriptpath = str(path[0]) + "/" + str(generatorname[0])
         else:
            scriptpath = "tasks/task" + str(TaskNr) + "/generator.sh"

         command = "sh "+ scriptpath + " " + str(UserId) + " " + str(TaskNr) + "  >> autosub.stdout 2>>autosub.stderr"
         generator_res = os.system(command)
         if generator_res:
            logmsg = "Failed to call generator script, return value: " + str(generator_res)
            self.log_a_msg(logmsg, "DEBUG")

         logmsg = "Generated individual task for user/tasknr:" + str(UserId) + "/" + str(TaskNr)
         self.log_a_msg(logmsg, "DEBUG")

         common.send_email(self.sender_queue, str(UserEmail), str(UserId), "Task", str(TaskNr), "Your personal example", str(MessageId))
