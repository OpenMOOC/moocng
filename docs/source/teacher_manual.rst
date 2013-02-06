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

There are three types of units: **normal**, **homeworks** and **exams**.

In a regular course the *normal* units are irrelevant when calculating the
course score. Because of this, their weights are automatically assumed as
zero, even if something else was specified when they were created by the
teachers. **In a regular course, only homeworks and exams counts**.

It is possible to specify that the *normal* units counts as well as the
*homeworks* or *exams*. This is knows as the old way of scoring courses, and
only an administrator of the system can activate this mode for a course.

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

TODO
