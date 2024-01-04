from ocpa.objects.log.util import misc as log_util
import random
import pandas as pd

def switch_activities(ocel, noise_level, allowed_switches):
    new_event_df = ocel.log.log.copy()
    new_rows = []

    for index, row in new_event_df.iterrows():
        applied_noise = False
        items = list(allowed_switches.items())
        #permutation of the object types
        items_perm = random.sample(items, len(items))
        for object_type, activity_pairs in items_perm:
            #permutation of activity pairs
            activity_pairs_perm = random.sample(activity_pairs, len(activity_pairs))
            for activity_pair in activity_pairs_perm:
                if not applied_noise:
                    if row['event_activity'] == activity_pair[0] and pd.notna(row[object_type]):
                        row_object_list = row[object_type]
                        if len(row_object_list) > 0 and random.random()<noise_level:
                            object_list = [o for o in row_object_list]
                            removed_object = random.choice(object_list)
                            object_list = [o for o in object_list if o != removed_object]

                            new_event_df.at[index,object_type] = object_list
                            new_row = row.copy()
                            new_row['event_activity'] = activity_pair[1]
                            new_row['event_timestamp'] = new_row['event_timestamp']+ pd.to_timedelta(1, unit='s')
                            new_row[object_type] = [removed_object]
                            for ot in ocel.object_types:
                                if ot!= object_type:
                                    new_row[ot] = []

                            # Add the new row to the list
                            new_rows.append(new_row)
                            applied_noise = True


    # Add new rows to the original DataFrame
    for new_row in new_rows:
        new_event_df = new_event_df.append(new_row, ignore_index=True)

    #sort by time
    new_event_df = new_event_df.sort_values(by='event_timestamp')
    new_event_df["event_id"] = list(range(1,len(new_event_df)+1))
    new_log = log_util.copy_log_from_df(new_event_df, ocel.parameters)
    return new_log

