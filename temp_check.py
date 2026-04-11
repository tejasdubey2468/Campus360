import os, sys
sys.path.insert(0, os.getcwd())
import StudentView.views as sv
import FacultyView.views as fv
print('sv present', sv.present)
print('fv has student_views', hasattr(fv, 'student_views'))
print('fv student_views present', fv.student_views.present)
sv.present.add('101')
print('after add sv present', sv.present)
print('after add fv student_views present', fv.student_views.present)
