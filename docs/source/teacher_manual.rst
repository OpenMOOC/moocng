===============
Teachers Manual
===============

Scoring
=======

Everything is scored in a 10 scale.

Course
------

The score of a student in a course is based on its units scores. The student
has a score in each unit, and those scores are properly ponderated. The score
of the course is just **the sum of the ponderated scores of the units**.

Unit
----

The score of a student in a unit is based on its nuggets' scores. Units have
weights, so there are two scores associated to them, the *raw* one, and the
ponderated.

The raw score of the unit is calculated adding the scores of the nuggets, that
have been properly ponderated. This score is not the real score of the student.
The ponderated one is.

To ponderate the score the system uses the weight assigned to the unit. Before
applying the weight, the platform normalized it. The weight is a percentage, so
all the units' weights together must sum a 100%, normalization ensures this.

Once the unit's weight is normalized, it is applied to the raw score, resulting
in the ponderated score of the unit. If the unit represents a 12% of the
course, the ponderated score of a perfect unit will be 1.2 over 10.

The units' scores are **the sum of their nuggets' scores, ponderated by the
unit's weight**.

Every unit counts?
~~~~~~~~~~~~~~~~~~

There are three types of units: **normal**, **homework** and **exams**.

In a regular course the *normal* units are irrelevant when calculating the
course score. Because of this, their weights are automatically assumed as
zero, even if something else was specified when they were created by the
teachers. **In a regular course, only homework and exams counts**.

It is possible to specify that the *normal* units counts as well as the
*homework* or *exams*. This is knows as the *old method* of scoring courses,
and only an administrator of the system can activate this mode for a course.

*Homeworks* and *exams* are identical when the scores are calculated. The
system expects the teachers to assign bigger weights to the *exams*.

Nugget
------

A nugget score relies on its question, which may not exist. As with units,
there are two scores for every nugget, a raw one and a ponderated one.

The raw scores are full or nothing, a 0 or a 10. **If the nugget has a question
then the score is 10 if the question is correct, and 0 if not**. There are not
partially correct question, the student must have answered perfectly the
question to score.

If nugget doesn't have a question, then its score is based on the activity of
the student. If the student has viewed the nugget then it's correct, if not
it's incorrect. Teachers will probably want to assign a zero or minimum weight
to these nuggets.

Progress
========

In the progress view of the courses is where the student can check how is he
doing. It's an overview of the student's scores, per unit.

There are two different progress bars in the view, one shows the *completion*
percentage of the unit, and the other shows the *correct* percentage of the
unit.

Completion
----------

The completion percentage is based on the student's activity. It counts the
number of nuggets in the unit, and the number of nuggets viewed by the student.
Each nuggets is ponderated based on its normalized weight, and then the
viewed or *completion* percentage is calculated.

**The completion percentage of a unit is the ponderated weights of the viewed
nuggets**.

Correction
----------

The *correct* percentage is based on the nuggets correction, which depends on
the nuggets having or not a question associated.

If a nugget has a question, then the nugget is correct if the question is
correct. There are not partially correct questions, the student must answer
perfectly the whole question.

If a nugget doesn't have a question, then the nugget is correct if the student
has viewed the nugget's video.

The percentage showed in the progress bar is calculated using the previous
conditions and ponderated weights of the nugget.

So, **the correction percentage of a unit is the ponderated weights of the
correct nuggets, a nugget is correct if its question is answered perfectly (if
any) or if its video is viewed (if there is no question)**.

Nuggets
-------

The list of the unit's nuggets is showed under the progress bars. And it shows
the **correction state of each nugget**, following the previously explained
criteria.

Example
=======

Our example course has two units with some nuggets:

- Unit A - Normal (15%)

  - Nugget A1 (30%)
  - Nugget A2 - Question A2Q (70%)

- Unit B - Exam (35%)

  - Nugget B1 (0%)
  - Nugget B2 - Question B2Q (50%)
  - Nugget B3 - Question B3Q (50%)

Let's see how the progress and score would be calculated for Bob, a student of
our course.

Bob enrolls in our course, and since he is very enthusiastic he starts
immediately with the first unit, the unit A.

The unit A is a *normal* unit, meaning that the scores in this course are
irrelevant for the course final score, unless the *old scoring method* is
activated for the course, which is not the case.

He starts viewing the video of the first nugget (A1). When the video is
finished he goes to the progress view to check if his activity has been
recorded.

In the progress view two bars are shown, and both are at 30%. The nugget
weights 30%, and after normalization the weight stays at 30%, since the weights
of the A unit sum a 100%. No normalization is needed in this case.

The nugget doesn't have a question, so viewed and correct are the same here.

After checking his progress, Bob returns to the classroom view to watch the
next nugget (A2). This time there is a question after the nugget to help Bob
realize his understanding of the concepts explained in unit A.

He answers it but fails, he hasn't properly understood one of the concepts
explained. He gets his answers immediately corrected and his mistake shown
because the unit is a *normal* one, without start or end dates, and the
questions of these units are no intend to be use as an evaluation tool, but
as reinforce of the student learning.

Bob goes to the progress view one more time, and now he sees that the
completion bar for the unit A is at 100%, but the correction bar is at 30%. He
goes back to the classroom and answers properly to the question this time,
since it is not homework or a exam, he can change his answer as many times as
he wants to. Now at the progress view he can see both bars at 100%.

Happy with these results, Bob navigates to the transcript view and checks his
scores. He has a 0. He understands that he has only completed a normal unit,
that doesn't count for the course score.

.. note::

   If the *old scoring method* were activated for the course, Bob would have
   found something different at the transcript view. Normal units would count,
   so the system would have taken the unit ponderated score and showed it. The
   unit has a weight of 15%, which when normalized changes to 30%. This happens
   because the both units don't sum a 100%, just a 50%. Since the unit
   ponderated weight is 30%, and Bob scored a 10 in the unit, the ponderated
   score would have been 3 over 10. And that would have been shown instead of
   0 if the *old method* was activated.

Bob goes again to the classroom and starts the next and last unit of the
course, the exam (B). But it happens that the exam doesn't start until the next
day, and will be open only 24 hours. This is a short course. Bob prepares
himself for the next day and goes to rest.

The next day Bob starts the exam. He views the first nugget (B1) which is an
introduction. The weight of the nugget is 0%, so nor the completion or the
correction bars advance in the progress view after he viewing the video.

He starts with the first question of the exam, the nugget B2. He answers the
question (B2Q) but his answer doesn't get corrected. He won't see the
correction until the end date for the exam is reached. He can change his answer
before that date, but he won't see a correction until after.

He answers as best as he knows, and then goes to the progress view. The
completion bar is at 50% and the correction bar at 0%. This doesn't mean that
Bob has answered wrongly, it's just that the unit is an exam, and until the
end date is reached no information about correction is shown.

Bob goes back to the classroom and answers the last question. At the progress
view the completion bar is now at 100%, but the correction bar stays at 0%. He
needs to wait until the next day to see the value of the correction bar.

Bob goes to rest, and wait for the due date of the exam. Hoping that he has
gotten the answer right.

The next day he goes to the transcript and he sees that he has a 5 over 10.
Sadly he had a mistake in one of the two questions. Then he goes to the
classroom to see what mistake has he made. He goes to the questions of the
exam and sees that he had the first question (B2Q) wrong. He changes his answer
and send it again, and this time the system corrects him but warns him that the
new answer won't be stored. The exams can only be answered between the start
and end dates.

.. note::

   If the *old scoring method* was activated, then he would have a 6.5 over 10
   instead. The unit A would count, and Bob scored a 10 in that unit. Unit A
   normalized weight is a 30%, so the 10 becomes a 3. Bob have scored a 5 in
   unit B, which normalized weight is 70%, so the 5 becomes a 3.5. The sum of
   the unit's normalized scores (3 and 3.5) results in a 6.5 over 10.

Bob checks the progress view and sees that for unit A both bars, completion and
correction, are at 100%. But for unit B the correction is at 50%, and the
completion at 100%.

Bob has completed the course now, and he has learned from his mistakes. He goes
and enrolls in another interesting course, hoping to achieve a perfect score
this time.

Assets
======

An asset can be defined as a (possibly) external resource which can be booked
by students. Examples of assets could be physical classrooms or virtual
videoconference rooms.

Making assets available to students
-----------------------------------

In order to make an asset available for students to reserve, the asset should
be linked to a nugget.

To do so, in the nugget administration page select *Save changes and add an
asset availability to this nugget*. Then a new tab will appear. There you
should be able to set in which dates assets might be booked through that nugget
and the list of assets made available to the students. To make an asset
available, select it in the asset list and click *Save changes and add an
asset*. To remove an asset, click the *Remove asset* button next to its name.

.. note::

   Be careful when changing the dates of the assets availability or making
   unavailable an asset, already existing reservations which are not compatible
   with the new availability will be automatically cancelled.

Assets properties
-----------------

All assets can be set a name and a description, the slot duration, as well as
a number of slots and the capacity of each slot, and the time in advance a
reservation or a cancellation requires.

A slot can be defined as the number of instances each asset can handle
simultaneusly. Examples of slot would be each room of a plant (provided they
have the same properties) or each instance of a virtual videoconference system.
The capacity is the number of students which can use a slot at the same time.

The slot duration is the time a reservation would last.

In order to edit the asset name, the asset description or the student capacity
of an asset which is bookable through a course, select the *Assets* page in the
*Course edition* section of the course administration.

Other asset parameters should be set by the site administrators.

The number of reservations each student can make can be set in the
*Information* page of the course administration interface.