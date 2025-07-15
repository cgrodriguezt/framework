PROCEDURE sp_replenish_tasks IS
       v_owner_id   NUMBER;
       v_depot_id   NUMBER;
       v_msg        VARCHAR2(2024);
  CURSOR c1 IS
  SELECT odp_owner_id
         , odp_depot_id
  FROM tmt_owner_depots
  WHERE odp_deleted = 'N'
        AND tmt_owner_depots.odp_replenish_tasks = 'Y';

 BEGIN
  OPEN c1;
  LOOP
   FETCH c1 INTO
    v_owner_id
   , v_depot_id;
   EXIT WHEN c1%notfound;
   BEGIN
    sp_create_replenish_jobs(
     v_owner_id
     , v_depot_id
     , 'system'
     , v_msg
    );
   EXCEPTION
    WHEN OTHERS THEN
     dbms_output.put_line('Process error ['
                          || TO_CHAR(sqlcode)
                          || ']: '
                          || substr(
      sqlerrm
      , 1
      , 256
     ));
   END;

  END LOOP;

  CLOSE c1;
 EXCEPTION
  WHEN OTHERS THEN
   dbms_output.put_line('Process error ['
                        || TO_CHAR(sqlcode)
                        || ']: '
                        || substr(
    sqlerrm
    , 1
    , 256
   ));
 END sp_replenish_tasks;